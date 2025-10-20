import os
# CRITICAL: Set environment variables BEFORE importing uagents
os.environ["DISABLE_ALMANAC"] = "true"
os.environ["MAILBOX_MODE"] = "true"

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
# Core dependencies
from dotenv import load_dotenv
from uagents import Agent, Context, Protocol, Model
import anthropic
import httpx

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CivicXAI_Provider")

# =====================================================
# 🔧 Configuration
# =====================================================

# Mailbox configuration (from documentation)
MAILBOX_SERVER = os.getenv("MAILBOX_SERVER", "https://mailbox.agentverse.ai")
MAILBOX_KEY = os.getenv("MAILBOX_KEY")  
PROVIDER_AGENT_PORT = int(os.getenv("PROVIDER_AGENT_PORT", 8002))
PROVIDER_AGENT_ENDPOINT = os.getenv("PROVIDER_AGENT_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# These are already set before import, but reinforce them
os.environ["DISABLE_ALMANAC"] = "true"
os.environ["MAILBOX_MODE"] = "true"
os.environ["MAILBOX_SERVER_URL"] = "https://agentverse.ai"


# Set default model based on available API
if ANTHROPIC_API_KEY:
    CHAT_MODEL = os.getenv("CHAT_MODEL", "claude-3-sonnet-20240229")
else:
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Agent Network Configuration
AGENT_NETWORK = os.getenv("AGENT_NETWORK", "testnet")
GATEWAY_AGENT_ADDRESS = os.getenv(
    "GATEWAY_AGENT_ADDRESS",
    "fetch15u55w0r7k2863gdy3jte03c75h58qnpxn0z3v2" # Matching the agent's own address for simplicity
)

# Cudos Configuration
CUDOS_NETWORK = os.getenv("CUDOS_NETWORK", "testnet")
CUDOS_RPC_ENDPOINT = os.getenv("CUDOS_RPC_ENDPOINT", "https://rpc.testnet.cudos.org")
CUDOS_REST_ENDPOINT = os.getenv("CUDOS_REST_ENDPOINT", "https://rest.testnet.cudos.org")

# Performance Configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 120))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))
# Performance Configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 120))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))

# =====================================================
# 📊 Pydantic Models for Agent Communication
# =====================================================
class AllocationRequest(Model):
    """Model for allocation requests from gateway."""
    request_id: str
    type: str
    region_id: str
    metrics: Dict[str, float]
    optimization: Dict[str, Any]
    notes: Optional[Dict[str, str]] = None
    files: Optional[List[Dict[str, Any]]] = None
    urls: Optional[List[Dict[str, str]]] = None
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
    files: Optional[List[Dict[str, Any]]] = None
    urls: Optional[List[Dict[str, str]]] = None
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
# 🤖 AI Processing Engine
# =====================================================
class AIProcessor:
    """
    Advanced AI processor using Claude for allocation analysis
    and explanation generation. Optimized for Cudos deployment.
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
    
    async def process_allocation_request(
        self, 
        request: AllocationRequest
    ) -> Dict[str, Any]:
        """
        Process allocation request using Claude AI.
        Analyzes metrics, files, and URLs to provide allocation recommendations.
        """
        start_time = datetime.now()
        
        try:
            async with self.request_semaphore:
                self.request_count += 1
                
                # Build context from all sources
                context = self._build_allocation_context(request)
                
                # Create prompt for Claude
                prompt = self._create_allocation_prompt(request, context)
                
                # Call Claude API with retry logic
                response = await self._call_claude_with_retry(prompt)
                
                # Parse and structure response
                result = self._parse_allocation_response(
                    response, 
                    request.optimization
                )
                
                self.success_count += 1
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "status": "success",
                    "recommendation": result,
                    "processing_time": processing_time,
                    "model": CHAT_MODEL,
                    "request_id": request.request_id
                }
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"Allocation processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "request_id": request.request_id
            }
    
    async def process_explanation_request(
        self, 
        request: ExplanationRequest
    ) -> Dict[str, Any]:
        """
        Generate explanation for allocation decision in requested language.
        """
        start_time = datetime.now()
        
        try:
            async with self.request_semaphore:
                self.request_count += 1
                
                # Build context
                context = self._build_explanation_context(request)
                
                # Create prompt
                prompt = self._create_explanation_prompt(request, context)
                
                # Call Claude
                response = await self._call_claude_with_retry(prompt)
                
                # Structure response
                result = {
                    "explanation": response,
                    "language": request.language,
                    "region_id": request.region_id,
                    "allocation_summary": request.allocation_data
                }
                
                self.success_count += 1
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "status": "success",
                    "explanation": result,
                    "processing_time": processing_time,
                    "model": CHAT_MODEL,
                    "request_id": request.request_id
                }
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"Explanation processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "request_id": request.request_id
            }
    
    def _build_allocation_context(self, request: AllocationRequest) -> str:
        """Build comprehensive context from all sources."""
        context_parts = []
        
        # Add metrics
        context_parts.append("## Regional Metrics")
        context_parts.append(f"Region: {request.region_id}")
        for key, value in request.metrics.items():
            context_parts.append(f"- {key.replace('_', ' ').title()}: {value:.2f}")
        
        # Add optimization results
        context_parts.append("\n## Optimization Analysis")
        opt = request.optimization
        context_parts.append(f"- Priority Score: {opt.get('priority_score', 0):.3f}")
        context_parts.append(f"- Risk-Adjusted Return: {opt.get('risk_adjusted_return', 0):.3f}")
        
        if 'components' in opt:
            context_parts.append("\n### Score Components:")
            for key, value in opt['components'].items():
                context_parts.append(f"  - {key.replace('_', ' ').title()}: {value:.3f}")
        
        # Add notes
        if request.notes:
            context_parts.append(f"\n## Additional Notes")
            context_parts.append(request.notes.get('content', ''))
            context_parts.append(f"Language: {request.notes.get('language', 'unknown')}")
        
        # Add file summaries
        if request.files:
            context_parts.append("\n## Processed Documents")
            for i, file in enumerate(request.files, 1):
                context_parts.append(f"\n### Document {i}: {file.get('filename', 'Unknown')}")
                context_parts.append(f"Language: {file.get('language', 'unknown')}")
                context_parts.append(f"Summary: {file.get('summary', 'No summary available')[:500]}")
        
        # Add URL contents
        if request.urls:
            context_parts.append("\n## Referenced Web Content")
            for i, url_data in enumerate(request.urls, 1):
                context_parts.append(f"\n### Source {i}: {url_data.get('url', 'Unknown')}")
                context_parts.append(f"Summary: {url_data.get('summary', 'No summary available')[:500]}")
        
        return "\n".join(context_parts)
    
    def _build_explanation_context(self, request: ExplanationRequest) -> str:
        """Build context for explanation generation."""
        context_parts = []
        
        context_parts.append(f"## Allocation Decision for {request.region_id}")
        context_parts.append(json.dumps(request.allocation_data, indent=2))
        
        if request.context:
            context_parts.append(f"\n## Additional Context")
            context_parts.append(request.context)
        
        if request.notes:
            context_parts.append(f"\n## Notes")
            context_parts.append(request.notes.get('content', ''))
        
        if request.files:
            context_parts.append("\n## Supporting Documents")
            for file in request.files:
                context_parts.append(f"- {file.get('filename')}: {file.get('summary', '')[:300]}")
        
        if request.urls:
            context_parts.append("\n## Reference Sources")
            for url_data in request.urls:
                context_parts.append(f"- {url_data.get('url')}: {url_data.get('summary', '')[:300]}")
        
        return "\n".join(context_parts)
    
    def _create_allocation_prompt(
        self, 
        request: AllocationRequest, 
        context: str
    ) -> str:
        """Create comprehensive prompt for allocation analysis."""
        return f"""You are an expert AI advisor for civic resource allocation and governance. 
Your role is to analyze regional data and provide evidence-based recommendations for resource allocation.

# Task
Analyze the following data and provide a comprehensive allocation recommendation for {request.region_id}.

# Context and Data
{context}

# Your Analysis Should Include:
1. **Priority Assessment**: Evaluate the overall priority score and its components
2. **Risk Analysis**: Assess corruption risk and mitigation strategies
3. **Impact Projection**: Estimate expected outcomes and benefits
4. **Resource Recommendations**: Specific allocation suggestions
5. **Implementation Strategy**: Practical steps for deployment
6. **Success Metrics**: How to measure impact
7. **Challenges and Mitigations**: Potential obstacles and solutions

# Output Format
Provide a structured JSON response with the following keys:
- priority_level: "high" | "medium" | "low"
- recommended_allocation_percentage: number (0-100)
- confidence_score: number (0-1)
- key_findings: array of strings
- recommendations: array of detailed recommendation objects
- risk_assessment: object with risk factors and mitigations
- expected_impact: object with quantitative and qualitative impacts
- implementation_timeline: object with phases and milestones
- monitoring_plan: array of metrics to track

Be data-driven, objective, and focus on maximizing social impact while minimizing risks."""
    
    def _create_explanation_prompt(
        self, 
        request: ExplanationRequest, 
        context: str
    ) -> str:
        """Create prompt for generating citizen-friendly explanations."""
        language_instructions = {
            "en": "in clear, simple English",
            "es": "en español claro y sencillo",
            "fr": "en français clair et simple",
            "sw": "kwa Kiswahili rahisi na wazi",
            "ar": "بالعربية الواضحة والبسيطة"
        }
        
        lang_instruction = language_instructions.get(
            request.language, 
            f"in clear, simple {request.language}"
        )
        
        return f"""You are a civic communication expert helping citizens understand government resource allocation decisions.

# Task
Explain the allocation decision {lang_instruction} in a way that is:
- Clear and accessible to non-experts
- Transparent about methodology and reasoning
- Honest about uncertainties and limitations
- Respectful and empathetic to community concerns

# Allocation Decision Context
{context}

# Your Explanation Should Cover:
1. **What was decided**: Clear statement of the allocation
2. **Why this decision**: Key factors and reasoning
3. **How it helps**: Expected benefits for the community
4. **What happens next**: Implementation steps
5. **How to provide feedback**: Citizen engagement mechanisms

# Tone Guidelines:
- Be conversational but professional
- Use analogies and examples when helpful
- Acknowledge concerns proactively
- Emphasize community benefits
- Build trust through transparency

# Output Format
Provide a well-structured explanation in {request.language} that a typical citizen can understand and trust."""
    
    async def _call_claude_with_retry(self, prompt: str) -> str:
        """Call Claude API with exponential backoff retry logic."""
        if not self.client:
            raise Exception("Anthropic API key not configured")
        
        for attempt in range(RETRY_ATTEMPTS):
            try:
                message = self.client.messages.create(
                    model=CHAT_MODEL,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return message.content[0].text
                
            except anthropic.RateLimitError as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"API error: {e}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        
        raise Exception("Max retry attempts exceeded")
    
    def _parse_allocation_response(
        self, 
        response: str, 
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse and validate Claude's allocation response."""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response
            
            parsed = json.loads(json_str)
            
            # Add optimization data
            parsed['optimization_score'] = optimization.get('priority_score', 0)
            parsed['risk_adjusted_return'] = optimization.get('risk_adjusted_return', 0)
            
            return parsed
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return structured text response
            return {
                "priority_level": "medium",
                "confidence_score": 0.7,
                "analysis": response,
                "optimization_score": optimization.get('priority_score', 0)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            "total_requests": self.request_count,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate": self.success_count / max(1, self.request_count),
            "model": CHAT_MODEL,
            "max_concurrent": MAX_CONCURRENT_REQUESTS
        }

# =====================================================
# 🌐 Cudos Integration Module
# =====================================================
class CudosIntegration:
    """
    Integration with Cudos network for decentralized compute.
    Handles network communication and resource management.
    """
    
    def __init__(self):
        self.network = CUDOS_NETWORK
        self.rpc_endpoint = CUDOS_RPC_ENDPOINT
        self.rest_endpoint = CUDOS_REST_ENDPOINT
        self.compute_jobs = {}
    
    async def register_compute_provider(self, agent_address: str) -> Dict[str, Any]:
        """Register as compute provider on Cudos network."""
        try:
            logger.info(f"Registering provider on Cudos {self.network}")
            
            # In production, this would interact with Cudos smart contracts
            # For now, we'll simulate registration
            registration = {
                "provider_address": agent_address,
                "network": self.network,
                "capabilities": [
                    "ai_inference",
                    "text_processing",
                    "multi_language_support"
                ],
                "pricing": {
                    "allocation_request": 0.1,  # CUDOS tokens
                    "explanation_request": 0.05
                },
                "registered_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            logger.info(f"✅ Registered on Cudos: {agent_address}")
            return registration
            
        except Exception as e:
            logger.error(f"Cudos registration error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def submit_compute_job(
        self, 
        job_id: str, 
        job_type: str, 
        data: Dict[str, Any]
    ) -> str:
        """Submit compute job to Cudos network."""
        self.compute_jobs[job_id] = {
            "type": job_type,
            "status": "processing",
            "submitted_at": datetime.now().isoformat(),
            "data": data
        }
        return job_id
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of compute job."""
        return self.compute_jobs.get(job_id, {"status": "not_found"})
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get Cudos network information."""
        return {
            "network": self.network,
            "rpc_endpoint": self.rpc_endpoint,
            "rest_endpoint": self.rest_endpoint,
            "active_jobs": len(self.compute_jobs),
            "status": "connected"
        }

# =====================================================
# 🤖 Provider Agent Setup
# =====================================================
# Globals
provider_agent: Optional[Agent] = None
ai_processor: Optional["AIProcessor"] = None
cudos_integration: Optional["CudosIntegration"] = None
async def initialize_provider():
    """Initialize provider agent and dependencies."""
    global provider_agent, ai_processor, cudos_integration  # << place first

    # Create the provider agent in local mode only
    # No mailbox = no Almanac registration attempts
    provider_agent = Agent(
        name="CivicXAI_Provider",
        seed="civic_xai_provider_seed_12345",  # Fixed seed for consistent address
        port=PROVIDER_AGENT_PORT,
        endpoint=[f"http://localhost:{PROVIDER_AGENT_PORT}"]
        # No mailbox parameter = runs locally only
    )

    print(f"✅ Provider agent address: {provider_agent.address}")

    # Initialize AI processor
    api_key = ANTHROPIC_API_KEY or OPENAI_API_KEY
    if api_key:
        ai_processor = AIProcessor(api_key)
        api_type = "Anthropic/Claude" if ANTHROPIC_API_KEY else "OpenAI/GPT"
        logger.info(f"✅ AI Processor initialized with {api_type}")
    else:
        logger.warning("⚠️ AI Processor not initialized - missing API key")
        logger.warning("   Set either OPENAI_API_KEY or ANTHROPIC_API_KEY in environment")

    # Initialize Cudos integration
    cudos_integration = CudosIntegration()
    await cudos_integration.register_compute_provider(provider_agent.address)

    logger.info(f"🚀 Provider agent initialized: {provider_agent.address}")
    logger.info(f"📡 Running in LOCAL MODE (no Almanac/mailbox)")
    logger.info(f"🔌 Port: {PROVIDER_AGENT_PORT}")
    logger.info(f"🌐 Endpoint: http://localhost:{PROVIDER_AGENT_PORT}")

# =====================================================
# 📨 Message Handlers Protocol
# =====================================================
provider_protocol = Protocol(name="CivicXAI_Provider_Protocol", version="2.0.0")

@provider_protocol.on_message(model=AllocationRequest)
async def handle_allocation_request(ctx: Context, sender: str, msg: AllocationRequest):
    """Handle allocation request from gateway."""
    logger.info(f"📥 Allocation request received: {msg.request_id} from {sender}")
    
    try:
        if not ai_processor:
            raise Exception("AI Processor not initialized")
        
        # Submit to Cudos compute network
        if cudos_integration:
            await cudos_integration.submit_compute_job(
                msg.request_id,
                "allocation_analysis",
                msg.dict()
            )
        
        # Process request
        result = await ai_processor.process_allocation_request(msg)
        
        # Create response
        response = AIResponse(
            request_id=msg.request_id,
            status=result["status"],
            response_type="allocation_recommendation",
            data=result.get("recommendation", {}),
            metadata={
                "processing_time": result["processing_time"],
                "model": result.get("model", "unknown"),
                "processor_stats": ai_processor.get_statistics()
            },
            timestamp=datetime.now().isoformat(),
            processing_time=result["processing_time"]
        )
        
        # Send response back to gateway
        await ctx.send(sender, response)
        logger.info(f"✅ Allocation response sent: {msg.request_id}")
        
    except Exception as e:
        logger.error(f"❌ Allocation processing failed: {e}")
        
        # Send error response
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
    logger.info(f"📥 Explanation request received: {msg.request_id} from {sender}")
    
    try:
        if not ai_processor:
            raise Exception("AI Processor not initialized")
        
        # Submit to Cudos
        if cudos_integration:
            await cudos_integration.submit_compute_job(
                msg.request_id,
                "explanation_generation",
                msg.dict()
            )
        
        # Process request
        result = await ai_processor.process_explanation_request(msg)
        
        # Create response
        response = AIResponse(
            request_id=msg.request_id,
            status=result["status"],
            response_type="explanation",
            data=result.get("explanation", {}),
            metadata={
                "processing_time": result["processing_time"],
                "model": result.get("model", "unknown"),
                "language": msg.language,
                "processor_stats": ai_processor.get_statistics()
            },
            timestamp=datetime.now().isoformat(),
            processing_time=result["processing_time"]
        )
        
        # Send response
        await ctx.send(sender, response)
        logger.info(f"✅ Explanation response sent: {msg.request_id}")
        
    except Exception as e:
        logger.error(f"❌ Explanation processing failed: {e}")
        
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

# =====================================================
# 📊 Status and Health Endpoints
# =====================================================
@provider_protocol.on_interval(period=60.0)
async def log_statistics(ctx: Context):
    """Log statistics periodically."""
    if ai_processor:
        stats = ai_processor.get_statistics()
        logger.info(f"📊 Stats - Requests: {stats['total_requests']}, "
                   f"Success: {stats['successful_requests']}, "
                   f"Rate: {stats['success_rate']:.2%}")
    
    if cudos_integration:
        cudos_info = cudos_integration.get_network_info()
        logger.info(f"🌐 Cudos - Jobs: {cudos_info['active_jobs']}, "
                   f"Status: {cudos_info['status']}")

# =====================================================
# 🚀 Main Application Entry Point
# =====================================================
async def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("🚀 Starting CivicXAI Provider Agent")
    logger.info("=" * 60)
    
    # Initialize provider
    await initialize_provider()
    
    # Include protocol without publishing to Almanac
    provider_agent.include(provider_protocol, publish_manifest=False)
    
    # Run agent
    logger.info("🏃 Agent running...")
    await provider_agent.run_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Provider agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise