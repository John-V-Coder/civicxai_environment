import requests
import os
import json
from dotenv import load_dotenv # To load environment variables from a .env file

# Load environment variables from .env file (for secure API key handling)
load_dotenv()

class ASIExplainAgent:
    def __init__(self, model_name="asi1-mini"):
        self.api_url = "https://api.asi1.ai/v1/chat/completions"
        self.api_key = os.getenv('ASI_ONE_API_KEY')
        self.model_name = model_name

        if not self.api_key:
            raise ValueError("ASI_ONE_API_KEY environment variable not set. Please create a .env file or set the variable.")

    def generate_explanation(self, region_data: dict, factors: dict, policy_feedback: str = None) -> str:
        """
        Generates a human-readable explanation for a funding allocation decision
        using the ASI:One chat completion API.

        Args:
            region_data (dict): A dictionary containing high-level information about the region,
                                e.g., {"region_name": "Kakamega", "priority_score": 0.85}.
            factors (dict): A dictionary of key factors and their influence,
                           e.g., {"deforestation": 0.45, "rainfall": 0.25}.
            policy_feedback (str, optional): Any feedback from the MeTTa policy engine,
                                             e.g., "Complies with eligibility rule: deforestation > 0.2".

        Returns:
            str: A natural language explanation for the decision.
        """

        # Construct a prompt for ASI:One based on the input data
        # This prompt is crucial for getting good explanations.
        prompt_parts = []
        if region_data.get("region_name"):
            prompt_parts.append(f"For {region_data['region_name']}:")
        if region_data.get("priority_score"):
            prompt_parts.append(f"The system calculated a priority score of {region_data['priority_score']:.2f}.")

        prompt_parts.append("This score was primarily influenced by the following factors:")
        for factor, value in factors.items():
            prompt_parts.append(f"- {factor.replace('_', ' ').capitalize()}: {value:.2f}")

        if policy_feedback:
            prompt_parts.append(f"It also aligns with the policy: '{policy_feedback}'.")

        prompt_parts.append("\nPlease provide a concise, citizen-friendly explanation (2-3 sentences) for this decision, highlighting the main reasons for the allocation.")

        user_content = " ".join(prompt_parts)

        body = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": user_content}]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=body)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            response_json = response.json()

            # Extract the content using the structure you provided
            if "choices" in response_json and len(response_json["choices"]) > 0:
                explanation = response_json["choices"][0]["message"]["content"]
                return explanation
            else:
                return "Failed to retrieve a valid explanation from ASI:One."

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return f"Error retrieving explanation: {str(e)}"
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return "Error: Invalid JSON response from API."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {str(e)}"

# Example Usage (for testing this module directly)
if __name__ == "__main__":
    # Create a .env file in civic-xai-environment/ containing:
    # ASI_ONE_API_KEY="your_asi_one_api_key_here"
    # Make sure to replace "your_asi_one_api_key_here" with your actual key.

    try:
        explain_agent = ASIExplainAgent()
        region_info = {"region_name": "Kakamega", "priority_score": 0.85}
        feature_factors = {"deforestation": 0.45, "rainfall": 0.25, "soil_quality": 0.10}
        policy_info = "Region is eligible for reforestation based on high deforestation rate."

        explanation = explain_agent.generate_explanation(region_info, feature_factors, policy_info)
        print("\n--- Generated Explanation ---")
        print(explanation)

        # Example with less detail
        region_info_less = {"region_name": "Turkana", "priority_score": 0.30}
        feature_factors_less = {"deforestation": 0.05, "rainfall": -0.15}
        explanation_less = explain_agent.generate_explanation(region_info_less, feature_factors_less)
        print("\n--- Generated Explanation (less detail) ---")
        print(explanation_less)

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An error occurred during example usage: {e}")
