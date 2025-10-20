import os
# CRITICAL: Set environment variables BEFORE importing uagents
os.environ["ALMANAC_API_DISABLED"] = "1"
os.environ["ALMANAC_DISABLED"] = "true"

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import uagents with minimal configuration
from uagents import Agent, Context, Protocol, Model
from uagents.setup import fund_agent_if_low

import anthropic

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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "claude-3-sonnet-20240229")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Cudos Configuration (simulated for now)
CUDOS_NETWORK = os.getenv("CUDOS_NETWORK", "testnet")

# Performance Configuration
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 5))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))

# =====================================================
# 📊 Pydantic Models
# =====================================================
class AllocationRequest(Model):
    """Model for allocation requests from gateway."""
    request_id: str
    type: str
    region_id: str
    metrics: Dict[str, float]
    optimization: Dict[str, Any]
    notes: Optional[Dict[str, str]] = None
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
# 🤖 Simplified AI Processor
# =====================================================
class AIProcessor:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.request_count = 0
        self.success_count = 0
    
    async def process_allocation_request(self, request: AllocationRequest) -> Dict[str, Any]:
        """Process allocation request."""
        start_time = datetime.now()
        
        try:
            self.request_count += 1
            
            # For demo purposes, return a mock response
            if not self.client:
                logger.warning("Using mock response - no API key configured")
                result = {
                    "priority_level": "high",
                    "recommended_allocation_percentage": 75.0,
                    "confidence_score": 0.85,
                    "key_findings": ["High need identified", "Good implementation capacity"],
                    "recommendations": [{"type": "immediate", "action": "Allocate resources"}]
                }
            else:
                # Real API call would go here
                prompt = f"Analyze allocation request for {request.region_id} with metrics: {request.metrics}"
                # Simplified for now
                result = {"priority_level": "medium", "confidence_score": 0.7}
            
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
            
            # Mock response for demonstration
            result = {
                "explanation": f"Allocation for {request.region_id} was made based on priority metrics.",
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
# 🤖 Agent Setup
# =====================================================
def create_agent():
    """Create the provider agent with minimal configuration."""
    try:
        # Create agent without seed to generate new address
        agent = Agent(
            name="CivicXAI_Provider",
            port=PROVIDER_AGENT_PORT,
            endpoint=[f"http://localhost:{PROVIDER_AGENT_PORT}"],
            mailbox=None  # No mailbox for now to avoid registration issues
        )
        
        logger.info(f"✅ Agent created with address: {agent.address}")
        logger.info(f"🔌 Running on port: {PROVIDER_AGENT_PORT}")
        
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise

# Initialize components
ai_processor = AIProcessor(ANTHROPIC_API_KEY or OPENAI_API_KEY)

# Create protocol
provider_protocol = Protocol(name="CivicXAI_Provider_Protocol", version="2.0.0")

@provider_protocol.on_message(model=AllocationRequest)
async def handle_allocation_request(ctx: Context, sender: str, msg: AllocationRequest):
    """Handle allocation request from gateway."""
    logger.info(f"📥 Allocation request: {msg.request_id} from {sender}")
    
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
        logger.info(f"✅ Response sent: {msg.request_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        
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
    logger.info(f"📥 Explanation request: {msg.request_id} from {sender}")
    
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
        logger.info(f"✅ Explanation sent: {msg.request_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        
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
    logger.info(f"📊 Stats - Requests: {stats['total_requests']}, "
               f"Success: {stats['successful_requests']}, "
               f"Rate: {stats['success_rate']:.2%}")

# =====================================================
# 🚀 Main Entry Point
# =====================================================
async def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("🚀 Starting CivicXAI Provider Agent (Simplified)")
    logger.info("=" * 60)
    
    # Create agent
    agent = create_agent()
    
    # Include protocol
    agent.include(provider_protocol, publish_manifest=False)
    
    # Run agent
    logger.info("🏃 Agent running...")
    logger.info(f"📡 Access at: http://localhost:{PROVIDER_AGENT_PORT}")
    logger.info("⚠️ Running without Almanac registration (local mode)")
    
    await agent.run_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Provider agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
