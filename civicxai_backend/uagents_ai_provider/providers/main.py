import os
# Enable Almanac registration for ASI network integration
# The agent will automatically request testnet tokens and register
# To disable registration, set ALMANAC_API_DISABLED=1 in .env file

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import uagents with minimal configuration
from uagents import Agent, Context, Protocol, Model

# Removed: import anthropic
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CivicXAI_Provider")

# Configuration
PROVIDER_AGENT_PORT = int(os.getenv("PROVIDER_AGENT_PORT", 8002))
AI_PROVIDER_AGENT_SEED = os.getenv("AI_PROVIDER_AGENT_SEED", "civic_xai_provider_seed_12345")  # Consistent seed for same address
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Removed: ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Default to gpt-4o-mini and strictly use OpenAI
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
if not CHAT_MODEL.startswith("gpt-") and not CHAT_MODEL.startswith("openai/"):
    logger.warning(f"CHAT_MODEL '{CHAT_MODEL}' does not look like an OpenAI model. Defaulting to gpt-4o-mini.")
    CHAT_MODEL = "gpt-4o-mini"
    
AI_PROVIDER = "openai"
AI_API_KEY = OPENAI_API_KEY

if not AI_API_KEY:
    logger.warning("OPENAI_API_KEY not configured. Running in mock mode.")

MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Cudos Configuration (simulated for now)
CUDOS_NETWORK = os.getenv("CUDOS_NETWORK", "testnet")

# Performance Configuration
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))

# =====================================================
# Pydantic Models (Unchanged)
# =====================================================
class AllocationRequest(Model):
    """Model for allocation requests from gateway."""
    request_id: str
    type: str
    region_id: str
    metrics: Dict[str, float]
    optimization: Dict[str, Any]
    notes: Optional[Dict[str, str]] = None
    files: Optional[list] = None  # Processed PDF/document data
    urls: Optional[list] = None   # URL content data
    timestamp: str

class ExplanationRequest(Model):
    """Model for explanation requests from gateway."""
    request_id: str
    type: str
    region_id: str
    allocation_data: Dict[str, Any]
    context: str
    language: str
    notes: Optional[Dict[str, str]] = None
    files: Optional[list] = None  # Processed PDF/document data
    urls: Optional[list] = None   # URL content data
    timestamp: str

class AIResponse(Model):
    """Model for AI responses back to gateway."""
    request_id: str
    status: str
    response_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str
    processing_time: float

# =====================================================
# Simplified AI Processor (Modified for OpenAI only)
# =====================================================
class AIProcessor:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider  # Will always be "openai" now
        self.model = model
        self.request_count = 0
        self.success_count = 0
        
        # Initialize the OpenAI client only
        if provider == "openai" and api_key:
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI client with model: {model}")
        else:
            self.client = None
            logger.warning("No OpenAI API client initialized - running in mock mode")
    
    async def process_allocation_request(self, request: AllocationRequest) -> Dict[str, Any]:
        """Process allocation request with PDF/URL context."""
        start_time = datetime.now()
        
        try:
            self.request_count += 1
            
            # Build context from all sources
            context_parts = [f"Region: {request.region_id}"]
            context_parts.append(f"Metrics: {request.metrics}")
            
            # Add PDF content if available
            if request.files:
                context_parts.append(f"\n{len(request.files)} documents provided:")
                for i, file in enumerate(request.files, 1):
                    # Use re.sub to ensure no newlines in summary that could break log/prompt formatting
                    summary = re.sub(r'\s+', ' ', file.get('summary', '')[:200]) 
                    context_parts.append(f"  - {file.get('filename')}: {summary}")
            
            # Add URL content if available
            if request.urls:
                context_parts.append(f"\n{len(request.urls)} URLs referenced:")
                for url_data in request.urls:
                    summary = re.sub(r'\s+', ' ', url_data.get('summary', '')[:200])
                    context_parts.append(f"  - {url_data.get('url')}: {summary}")
            
            context = "\n".join(context_parts)
            
            # For demo purposes, return a mock response
            if not self.client:
                logger.warning("Using mock response - no API key configured")
                result = {
                    "priority_level": "high",
                    "recommended_allocation_percentage": 75.0,
                    "confidence_score": 0.85,
                    "key_findings": ["High need identified", "Good implementation capacity"],
                    "recommendations": [{"type": "immediate", "action": "Allocate resources"}],
                    "documents_analyzed": len(request.files) if request.files else 0,
                    "urls_analyzed": len(request.urls) if request.urls else 0
                }
            else:
                # Real API call with full context (OpenAI only)
                prompt = f"""Analyze this resource allocation request and provide recommendations:

{context}

Please provide:
1. Priority level (low/medium/high)
2. Recommended allocation percentage (0-100)
3. Confidence score (0-1)
4. Key findings (3-5 points)
5. Specific recommendations

Format your entire response as a single, valid JSON object, without any surrounding text or markdown, for easy machine parsing."""
                
                logger.info(f"Processing with {self.provider} using {self.model}")
                logger.info(f"Context: {len(request.files or [])} docs, {len(request.urls or [])} URLs")
                
                try:
                    # OpenAI API Call
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an expert in resource allocation and policy analysis. Provide data-driven recommendations. Respond only with a valid JSON object."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                        response_format={"type": "json_object"} # Use json_object for better parsing
                    )
                    ai_response_content = response.choices[0].message.content
                    
                except Exception as api_e:
                    logger.error(f"OpenAI API call failed: {api_e}")
                    raise api_e

                # Try to parse JSON response
                try:
                    if ai_response_content:
                        # Since we used response_format={"type": "json_object"}, it should be clean JSON
                        parsed = json.loads(ai_response_content)
                        result = {
                            "priority_level": parsed.get("priority_level", "medium"),
                            "recommended_allocation_percentage": parsed.get("recommended_allocation_percentage", 50.0),
                            "confidence_score": parsed.get("confidence_score", 0.7),
                            "key_findings": parsed.get("key_findings", []),
                            "recommendations": parsed.get("recommendations", []),
                            "ai_analysis": ai_response_content,
                            "documents_analyzed": len(request.files) if request.files else 0,
                            "urls_analyzed": len(request.urls) if request.urls else 0
                        }
                    else:
                        result = {
                            "priority_level": "medium",
                            "confidence_score": 0.7,
                            "documents_analyzed": len(request.files) if request.files else 0,
                            "urls_analyzed": len(request.urls) if request.urls else 0
                        }
                except json.JSONDecodeError:
                    # If JSON parsing fails (despite response_format), return raw response
                    result = {
                        "priority_level": "medium",
                        "confidence_score": 0.7,
                        "ai_analysis": ai_response_content,
                        "documents_analyzed": len(request.files) if request.files else 0,
                        "urls_analyzed": len(request.urls) if request.urls else 0
                    }
            
            self.success_count += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "recommendation": result,
                "processing_time": processing_time,
                "request_id": request.request_id
            }
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "request_id": request.request_id
            }
    
    async def process_explanation_request(self, request: ExplanationRequest) -> Dict[str, Any]:
        """Generate explanation for allocation decision."""
        start_time = datetime.now()
        
        try:
            self.request_count += 1
            
            # --- Modified to use OpenAI for explanation if client is available ---
            if not self.client:
                logger.warning("Using mock explanation response - no API key configured")
                explanation_text = f"Allocation for {request.region_id} was made based on priority metrics (mocked response)."
            else:
                prompt = f"""Given the following allocation data and context, provide a clear, concise explanation of the decision in {request.language}.

Allocation Data: {json.dumps(request.allocation_data)}
Context: {request.context}

Please generate an explanation suitable for a public audience. Focus on the 'key_findings' and 'recommendations' from the allocation data."""
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": f"You are a public communication expert. Provide a clear and concise explanation for a resource allocation decision in {request.language}."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS // 2 # Use fewer tokens for explanation
                    )
                    explanation_text = response.choices[0].message.content
                except Exception as api_e:
                    logger.error(f"OpenAI Explanation API call failed: {api_e}")
                    explanation_text = f"Allocation explanation failed due to API error: {str(api_e)}"
            
            result = {
                "explanation": explanation_text,
                "language": request.language,
                "region_id": request.region_id,
                "allocation_summary": request.allocation_data
            }
            # ---------------------------------------------------------------------

            self.success_count += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "explanation": result,
                "processing_time": processing_time,
                "request_id": request.request_id
            }
        except Exception as e:
            logger.error(f"Explanation error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "request_id": request.request_id
            }

# =====================================================
# Agent Setup (Unchanged)
# =====================================================
def create_agent():
    """Create the provider agent with Almanac registration enabled."""
    try:
        # Create agent with seed for consistent address
        agent = Agent(
            name="CivicXAI_Provider",
            seed=AI_PROVIDER_AGENT_SEED,
            port=PROVIDER_AGENT_PORT,
            endpoint=[f"http://localhost:{PROVIDER_AGENT_PORT}"]
        )
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise

# Initialize components
ai_processor = AIProcessor(AI_PROVIDER, AI_API_KEY, CHAT_MODEL)

# Create protocol (Unchanged)
provider_protocol = Protocol(name="CivicXAI_Provider_Protocol", version="2.0.0")

@provider_protocol.on_message(model=AllocationRequest)
async def handle_allocation_request(ctx: Context, sender: str, msg: AllocationRequest):
    """Handle allocation request from gateway."""
    logger.info(f"Allocation request: {msg.request_id} from {sender}")
    
    try:
        result = await ai_processor.process_allocation_request(msg)
        
        response = AIResponse(
            request_id=msg.request_id,
            status=result["status"],
            response_type="allocation_recommendation",
            data=result.get("recommendation", {}),
            metadata={
                "processing_time": result["processing_time"],
                "model": CHAT_MODEL
            },
            timestamp=datetime.now().isoformat(),
            processing_time=result["processing_time"]
        )
        
        await ctx.send(sender, response)
        logger.info(f"Response sent: {msg.request_id}")
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        
        error_response = AIResponse(
            request_id=msg.request_id,
            status="error",
            response_type="allocation_recommendation",
            data={"error": str(e)},
            metadata={"error_type": type(e).__name__},
            timestamp=datetime.now().isoformat(),
            processing_time=0.0
        )
        
        await ctx.send(sender, error_response)

@provider_protocol.on_message(model=ExplanationRequest)
async def handle_explanation_request(ctx: Context, sender: str, msg: ExplanationRequest):
    """Handle explanation request from gateway."""
    logger.info(f"Explanation request: {msg.request_id} from {sender}")
    
    try:
        result = await ai_processor.process_explanation_request(msg)
        
        response = AIResponse(
            request_id=msg.request_id,
            status=result["status"],
            response_type="explanation",
            data=result.get("explanation", {}),
            metadata={
                "processing_time": result["processing_time"],
                "model": CHAT_MODEL,
                "language": msg.language
            },
            timestamp=datetime.now().isoformat(),
            processing_time=result["processing_time"]
        )
        
        await ctx.send(sender, response)
        logger.info(f"Explanation sent: {msg.request_id}")
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        
        error_response = AIResponse(
            request_id=msg.request_id,
            status="error",
            response_type="explanation",
            data={"error": str(e)},
            metadata={"error_type": type(e).__name__},
            timestamp=datetime.now().isoformat(),
            processing_time=0.0
        )
        
        await ctx.send(sender, error_response)

@provider_protocol.on_interval(period=60.0)
async def log_statistics(ctx: Context):
    """Log statistics periodically."""
    stats = {
        "total_requests": ai_processor.request_count,
        "successful_requests": ai_processor.success_count,
        "success_rate": ai_processor.success_count / max(1, ai_processor.request_count)
    }
    logger.info(f"Stats - Requests: {stats['total_requests']}, "
               f"Success: {stats['successful_requests']}, "
               f"Rate: {stats['success_rate']:.2%}")

# =====================================================
# Main Entry Point (Unchanged)
# =====================================================
async def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info(" Starting CivicXAI Provider Agent (OpenAI Only)")
    logger.info("=" * 60)
    
    # Create agent
    agent = create_agent()
    
    # Include protocol
    agent.include(provider_protocol, publish_manifest=False)
    
    # Log detailed agent information
    logger.info(f"Agent created with address: {agent.address}")
    
    # Create agent inspector URL
    import urllib.parse
    endpoint_encoded = urllib.parse.quote(f"http://127.0.0.1:{PROVIDER_AGENT_PORT}", safe='')
    inspector_url = f"https://agentverse.ai/inspect/?uri={endpoint_encoded}&address={agent.address}"
    logger.info(f"Agent inspector available at {inspector_url}")
    
    # Log server information
    logger.info(f"Starting server on http://0.0.0.0:{PROVIDER_AGENT_PORT} (Press CTRL+C to quit)")
    
    # Get ASI network address (Fetch wallet address)
    try:
        wallet_address = agent.wallet.address()
        logger.info(f"ASI network address: {wallet_address}")
        
        # Try to get balance
        try:
            balance = agent.wallet.balance()
            logger.info(f"Balance of addr: {balance}")
        except Exception as e:
            logger.info(f"Balance of addr: [Not yet available - will update after registration]")
    except Exception as e:
        logger.warning(f"Could not retrieve wallet info: {e}")
    
    logger.info(" Almanac registration enabled - testnet tokens will be requested automatically")
    logger.info(" View your agent at: https://agentverse.ai")
    logger.info("=" * 60)
    
    await agent.run_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nProvider agent stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise