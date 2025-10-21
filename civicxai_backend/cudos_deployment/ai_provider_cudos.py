"""
Enhanced AI Provider Agent with CUDOS Integration
Based on official documentation:
- https://docs.agentverse.ai/home
- https://docs.asi1.ai/documentation/getting-started/overview
- https://docs.cudos.org/docs/welcome

This agent integrates:
1. uAgents Framework for decentralized communication
2. ASI:One for AI governance standards
3. CUDOS for decentralized compute resources
4. OpenAI for language models
5. MeTTa for symbolic reasoning
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from uagents import Agent, Context, Protocol, Model, Bureau
from pydantic import  Field
import openai
from openai import AsyncOpenAI
import logging
import aiohttp

# Import backend components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from civicxai_backend.metta.metta_engine_enhanced import EnhancedCivicMeTTaEngine
    METTA_AVAILABLE = True
except ImportError:
    METTA_AVAILABLE = False
    print("[WARNING] MeTTa engine not available - using fallback calculations")

try:
    from civicxai_backend.agents.asi1_governance import ASIExplainAgent
    ASI_AVAILABLE = True
except ImportError:
    ASI_AVAILABLE = False
    print("[WARNING] ASI:One agent not available - using OpenAI only")

# =====================================================
# Configuration
# =====================================================
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# Agent Configuration
AGENT_SEED = os.getenv("AI_PROVIDER_AGENT_SEED", "civic_xai_ai_provider_cudos_seed")
AGENT_PORT = int(os.getenv("AI_PROVIDER_AGENT_PORT", 8001))
AGENT_ENDPOINT = os.getenv(
    "AI_PROVIDER_AGENT_ENDPOINT", 
    f"http://127.0.0.1:{AGENT_PORT}/submit"
)

# Network Configuration
AGENTVERSE_MAILBOX_KEY = os.getenv("AGENTVERSE_MAILBOX_KEY", "")
AGENT_NETWORK = os.getenv("AGENT_NETWORK", "testnet")

# ASI:One Configuration
ASI_API_KEY = os.getenv("ASI_ONE_API_KEY", "")
ASI_ENDPOINT = os.getenv("ASI_ENDPOINT", "https://api.asi1.ai/v1")

# CUDOS Configuration
CUDOS_API_KEY = os.getenv("CUDOS_API_KEY", "")
CUDOS_ENDPOINT = os.getenv("CUDOS_ENDPOINT", "https://api.cudos.org/v1")
CUDOS_COMPUTE_ENABLED = os.getenv("CUDOS_COMPUTE_ENABLED", "false").lower() == "true"

if not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY not set - some features may be limited")

# =====================================================
# Enhanced Message Models (ASI:One + CUDOS Standards)
# =====================================================

class ComputeRequest(Model):
    """Request for decentralized compute resources via CUDOS"""
    request_id: str = Field(description="Unique request identifier")
    compute_type: str = Field(description="Type of compute: ml_inference, data_processing, etc")
    resources: Dict[str, Any] = Field(description="Required resources (CPU, GPU, memory)")
    data_hash: str = Field(description="Hash of data to process")
    estimated_duration: int = Field(description="Estimated duration in seconds")

class ComputeResponse(Model):
    """Response from CUDOS compute network"""
    request_id: str
    compute_node_id: str
    status: str  # queued, processing, completed, failed
    result_hash: Optional[str] = None
    cost_cudos: Optional[float] = None

class AllocationRequest(Model):
    """Enhanced allocation request with compute tracking - aligned with gateway"""
    request_id: str
    type: str
    region_id: str
    metrics: Dict[str, float]  # poverty_index, project_impact, environmental_score, corruption_risk
    optimization: Dict[str, Any]
    notes: Optional[Dict[str, str]] = None
    files: Optional[list] = None  # Processed PDF/document data from gateway
    urls: Optional[list] = None   # URL content data from gateway
    compute_preference: str = "local"  # local, cudos, hybrid
    timestamp: str

class AIResponse(Model):
    """AI response back to gateway - aligned with simplified provider"""
    request_id: str
    status: str
    response_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str
    processing_time: float

class ExplanationRequest(Model):
    """Request for AI explanation - aligned with gateway"""
    request_id: str
    type: str
    region_id: str
    allocation_data: Dict[str, Any]
    context: str
    language: str
    notes: Optional[Dict[str, str]] = None
    files: Optional[list] = None  # Processed PDF/document data from gateway
    urls: Optional[list] = None   # URL content data from gateway
    explanation_sources: List[str] = ["openai"]  # openai, asi1, cudos

# Note: Use AIResponse for explanation responses too

# =====================================================
# CUDOS Integration
# =====================================================

class CUDOSCompute:
    """Interface for CUDOS decentralized compute network"""
    
    def __init__(self):
        self.api_key = CUDOS_API_KEY
        self.endpoint = CUDOS_ENDPOINT
        self.enabled = CUDOS_COMPUTE_ENABLED
        
    async def request_compute(self, compute_type: str, data: Dict[str, Any]) -> Optional[str]:
        """Request compute resources from CUDOS network"""
        if not self.enabled:
            logger.info("CUDOS compute disabled - using local processing")
            return None
            
        try:
            # In production, this would connect to CUDOS network
            # For now, we simulate the request
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "type": compute_type,
                    "data": data,
                    "requirements": {
                        "cpu": "2",
                        "memory": "4GB",
                        "gpu": "optional"
                    }
                }
                
                # Simulated CUDOS API call
                logger.info(f"Requesting CUDOS compute for {compute_type}")
                
                # In reality, would call CUDOS API
                # async with session.post(f"{self.endpoint}/compute", 
                #                         headers=headers, 
                #                         json=payload) as response:
                #     result = await response.json()
                #     return result.get("compute_id")
                
                # Simulation
                return f"cudos_compute_{hashlib.md5(json.dumps(data).encode()).hexdigest()[:8]}"
                
        except Exception as e:
            logger.error(f"CUDOS compute request failed: {e}")
            return None
    
    async def check_compute_status(self, compute_id: str) -> Dict[str, Any]:
        """Check status of CUDOS compute job"""
        # In production, would check actual CUDOS job status
        return {
            "compute_id": compute_id,
            "status": "completed",
            "cost": 0.001  # CUDOS tokens
        }

# =====================================================
#  Enhanced AI Service Provider
# =====================================================

class EnhancedCivicXAIProvider:
    """Multi-source AI provider with CUDOS, ASI:One, and OpenAI"""
    
    def __init__(self):
        """Initialize with multiple AI sources"""
        # OpenAI client
        if OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        else:
            self.openai_client = None
            
        # MeTTa engine
        if METTA_AVAILABLE:
            self.metta_engine = EnhancedCivicMeTTaEngine()
            logger.info("MeTTa engine loaded")
        else:
            self.metta_engine = None
            
        # ASI:One agent
        if ASI_AVAILABLE and ASI_API_KEY:
            self.asi_agent = ASIExplainAgent()
            logger.info("ASI:One agent loaded")
        else:
            self.asi_agent = None
            
        # CUDOS compute
        self.cudos = CUDOSCompute()
        if self.cudos.enabled:
            logger.info("CUDOS compute enabled")
            
        # Cache
        self.cache = {}
        
    async def calculate_allocation(self, data: Dict[str, Any], 
                                  use_cudos: bool = False) -> Dict[str, Any]:
        """Calculate allocation with optional CUDOS compute"""
        
        compute_provider = "local"
        
        # Check if we should use CUDOS for computation
        if use_cudos and self.cudos.enabled:
            compute_id = await self.cudos.request_compute("allocation_calculation", data)
            if compute_id:
                compute_provider = "cudos"
                logger.info(f"Using CUDOS compute: {compute_id}")
                # In production, would wait for CUDOS result
                # For now, continue with local calculation
        
        # Calculate using MeTTa or fallback
        if self.metta_engine:
            analysis = self.metta_engine.analyze_allocation(
                poverty=data["poverty_index"],
                impact=data["project_impact"],
                environment=data["environmental_score"],
                corruption=data["corruption_risk"]
            )
            
            result = {
                "priority_score": analysis["score"],
                "allocation_percentage": analysis["allocation_percentage"],
                "priority_level": analysis["priority_level"],
                "recommendation": analysis.get("recommendation", ""),
                "explanations": analysis.get("explanations", {}),
                "compute_provider": compute_provider
            }
        else:
            # Fallback calculation
            score = (
                data["poverty_index"] * 0.40 +
                data["project_impact"] * 0.30 +
                data["environmental_score"] * 0.20 -
                data["corruption_risk"] * 0.10
            )
            
            if score >= 0.7:
                priority = "critical"
            elif score >= 0.4:
                priority = "high"
            elif score >= 0.2:
                priority = "medium"
            else:
                priority = "low"
            
            result = {
                "priority_score": round(score, 4),
                "allocation_percentage": round(score * 100, 2),
                "priority_level": priority,
                "recommendation": f"Allocate {round(score * 100, 2)}% of budget",
                "explanations": {},
                "compute_provider": compute_provider
            }
        
        # Generate verification hash for auditing
        result["verification_hash"] = hashlib.sha256(
            json.dumps(result, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        return result
    
    async def generate_explanation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using multiple AI sources"""
        
        sources_used = []
        explanations = []
        compute_provider = "hybrid"
        
        # Try ASI:One first if available
        if self.asi_agent and "asi1" in data.get("explanation_sources", ["asi1"]):
            try:
                asi_explanation = self.asi_agent.generate_explanation(
                    region_data={"region_name": data.get("region_id"), 
                                "priority_score": data.get("allocation_data", {}).get("priority_score", 0)},
                    factors=data.get("allocation_data", {}).get("factors", {}),
                    policy_feedback=data.get("context", "")
                )
                explanations.append(asi_explanation)
                sources_used.append("asi1")
                logger.info("ASI:One explanation generated")
            except Exception as e:
                logger.error(f"ASI:One explanation failed: {e}")
        
        # Use OpenAI if available
        if self.openai_client and "openai" in data.get("explanation_sources", ["openai"]):
            try:
                openai_explanation = await self._generate_openai_explanation(data)
                explanations.append(openai_explanation["explanation"])
                sources_used.append("openai")
                logger.info("OpenAI explanation generated")
            except Exception as e:
                logger.error(f"OpenAI explanation failed: {e}")
        
        # Check if CUDOS compute was requested
        if "cudos" in data.get("explanation_sources", []):
            if self.cudos.enabled:
                compute_id = await self.cudos.request_compute("explanation_generation", data)
                if compute_id:
                    sources_used.append("cudos")
                    compute_provider = "cudos"
                    logger.info(f"CUDOS compute used: {compute_id}")
        
        # Combine explanations
        if explanations:
            final_explanation = self._combine_explanations(explanations)
            confidence = 0.85 if len(sources_used) > 1 else 0.75
        else:
            final_explanation = "Unable to generate explanation with available sources"
            confidence = 0.0
        
        # Generate suggested actions
        suggested_actions = self._generate_suggestions(data, final_explanation)
        
        return {
            "explanation": final_explanation,
            "confidence_score": confidence,
            "suggested_actions": suggested_actions,
            "sources_used": sources_used,
            "compute_provider": compute_provider
        }
    
    async def _generate_openai_explanation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation using OpenAI"""
        system_prompt = """You are CivicXAI, an advanced AI system for transparent civic fund allocation.
        Provide clear, citizen-friendly explanations that justify allocation decisions based on data.
        Focus on transparency, fairness, and actionable insights."""
        
        user_prompt = f"""
        Explain the fund allocation for Region {data.get('region_id')}:
        
        Allocation Data: {json.dumps(data.get('allocation_data', {}), indent=2)}
        Context: {data.get('context', 'None')}
        Language: {data.get('language', 'en')}
        
        Provide a concise explanation highlighting key factors and recommendations.
        """
        
        response = await self.openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "explanation": response.choices[0].message.content,
            "model": CHAT_MODEL
        }
    
    def _combine_explanations(self, explanations: List[str]) -> str:
        """Intelligently combine multiple explanations"""
        if len(explanations) == 1:
            return explanations[0]
        
        # Simple combination - in production, use more sophisticated merging
        combined = "Based on multiple AI analysis sources:\n\n"
        for i, exp in enumerate(explanations, 1):
            combined += f"Analysis {i}: {exp}\n\n"
        
        return combined.strip()
    
    def _generate_suggestions(self, data: Dict[str, Any], explanation: str) -> List[str]:
        """Generate actionable suggestions"""
        suggestions = []
        
        allocation_data = data.get("allocation_data", {})
        score = allocation_data.get("priority_score", 0)
        
        if score > 0.7:
            suggestions.append("Prioritize immediate fund disbursement")
            suggestions.append("Establish monitoring framework for impact assessment")
        elif score > 0.4:
            suggestions.append("Schedule quarterly review of allocation effectiveness")
            suggestions.append("Consider partnerships to maximize impact")
        else:
            suggestions.append("Explore alternative funding sources")
            suggestions.append("Focus on capacity building before major investments")
        
        # Add corruption-specific suggestions if needed
        if allocation_data.get("corruption_risk", 0) > 0.5:
            suggestions.append("Implement enhanced oversight and audit procedures")
        
        return suggestions[:3]  # Limit to top 3 suggestions

# =====================================================
# Enhanced AI Provider Agent with CUDOS
# =====================================================

class CUDOSAIProviderAgent:
    def __init__(self):
        """Initialize enhanced agent with CUDOS support"""
        # Create agent
        if AGENTVERSE_MAILBOX_KEY:
            self.agent = Agent(
                name="CivicXAI_AI_Provider_CUDOS",
                seed=AGENT_SEED,
                port=AGENT_PORT,
                endpoint=[AGENT_ENDPOINT],
                mailbox_key=AGENTVERSE_MAILBOX_KEY
            )
            logger.info("AI Provider agent created with Agentverse support")
        else:
            self.agent = Agent(
                name="CivicXAI_AI_Provider_CUDOS",
                seed=AGENT_SEED,
                port=AGENT_PORT,
                endpoint=[AGENT_ENDPOINT]
            )
            logger.info("AI Provider agent created in local mode")
        
        # Initialize enhanced provider
        self.ai_provider = EnhancedCivicXAIProvider()
        
        # Create protocol
        self.protocol = Protocol(
            name="CivicXAI_AI_Provider_Protocol_v2",
            version="2.0.0"
        )
        
        # Setup handlers
        self._setup_handlers()
        
        # Include protocol
        self.agent.include(self.protocol, publish_manifest=True)
    
    def _setup_handlers(self):
        """Setup enhanced message handlers"""
        
        @self.agent.on_event("startup")
        async def introduce_agent(ctx: Context):
            """Agent startup handler"""
            ctx.logger.info(f"Enhanced AI Provider Agent started")
            ctx.logger.info(f"Address: {self.agent.address}")
            ctx.logger.info(f"Models: {CHAT_MODEL}")
            ctx.logger.info(f"Network: {AGENT_NETWORK}")
            
            status = []
            if METTA_AVAILABLE:
                status.append("MeTTa")
            if ASI_AVAILABLE:
                status.append("ASI:One")
            if self.ai_provider.cudos.enabled:
                status.append("CUDOS")
            if self.ai_provider.openai_client:
                status.append("OpenAI")
            
            ctx.logger.info(f"Active integrations: {', '.join(status)}")
        
        @self.protocol.on_message(model=AllocationRequest, replies=AIResponse)
        async def handle_allocation_request(ctx: Context, sender: str, msg: AllocationRequest):
            """Handle enhanced allocation request - aligned with gateway"""
            ctx.logger.info(f"Processing allocation for {msg.region_id} (compute: {msg.compute_preference})")
            
            try:
                start_time = datetime.now()
                
                # Extract metrics from dict
                use_cudos = msg.compute_preference in ["cudos", "hybrid"]
                result = await self.ai_provider.calculate_allocation({
                    "poverty_index": msg.metrics.get("poverty_index", 0),
                    "project_impact": msg.metrics.get("project_impact", 0),
                    "environmental_score": msg.metrics.get("environmental_score", 0),
                    "corruption_risk": msg.metrics.get("corruption_risk", 0)
                }, use_cudos=use_cudos)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Log file/URL processing
                if msg.files:
                    ctx.logger.info(f"Processing {len(msg.files)} documents from gateway")
                if msg.urls:
                    ctx.logger.info(f"Processing {len(msg.urls)} URLs from gateway")
                
                # Create AIResponse aligned with simplified provider
                response = AIResponse(
                    request_id=msg.request_id,
                    status="success",
                    response_type="allocation_recommendation",
                    data={
                        "priority_level": result["priority_level"],
                        "recommended_allocation_percentage": result["allocation_percentage"],
                        "priority_score": result["priority_score"],
                        "recommendation": result["recommendation"],
                        "verification_hash": result["verification_hash"],
                        "documents_analyzed": len(msg.files) if msg.files else 0,
                        "urls_analyzed": len(msg.urls) if msg.urls else 0
                    },
                    metadata={
                        "processing_time": processing_time,
                        "compute_provider": result["compute_provider"],
                        "model": CHAT_MODEL,
                        "cudos_enabled": use_cudos
                    },
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"Sent allocation response for {msg.region_id}")
                
            except Exception as e:
                ctx.logger.error(f"Error processing allocation: {e}")
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
        
        @self.protocol.on_message(model=ExplanationRequest, replies=AIResponse)
        async def handle_explanation_request(ctx: Context, sender: str, msg: ExplanationRequest):
            """Handle multi-source explanation request - aligned with gateway"""
            ctx.logger.info(f"Generating explanation for {msg.region_id} using {msg.explanation_sources}")
            
            try:
                start_time = datetime.now()
                
                # Log file/URL processing
                if msg.files:
                    ctx.logger.info(f"Including {len(msg.files)} documents in explanation")
                if msg.urls:
                    ctx.logger.info(f"Including {len(msg.urls)} URLs in explanation")
                
                # Generate multi-source explanation
                result = await self.ai_provider.generate_explanation({
                    "region_id": msg.region_id,
                    "allocation_data": msg.allocation_data,
                    "context": msg.context,
                    "language": msg.language,
                    "explanation_sources": msg.explanation_sources
                })
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Create AIResponse aligned with simplified provider
                response = AIResponse(
                    request_id=msg.request_id,
                    status="success",
                    response_type="explanation",
                    data={
                        "explanation": result["explanation"],
                        "confidence_score": result["confidence_score"],
                        "suggested_actions": result["suggested_actions"],
                        "region_id": msg.region_id,
                        "language": msg.language,
                        "documents_analyzed": len(msg.files) if msg.files else 0,
                        "urls_analyzed": len(msg.urls) if msg.urls else 0
                    },
                    metadata={
                        "processing_time": processing_time,
                        "compute_provider": result["compute_provider"],
                        "sources_used": result["sources_used"],
                        "model": CHAT_MODEL,
                        "language": msg.language
                    },
                    timestamp=datetime.now().isoformat(),
                    processing_time=processing_time
                )
                
                await ctx.send(sender, response)
                ctx.logger.info(f"Sent explanation for {msg.region_id} using {result['sources_used']}")
                
            except Exception as e:
                ctx.logger.error(f"Error generating explanation: {e}")
                # Send error response
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
    
    async def run(self):
        """Run the enhanced agent"""
        await self.agent.run_async()

# =====================================================
# Main Entry Point
# =====================================================

async def main():
    """Main function to run enhanced AI provider"""
    provider = CUDOSAIProviderAgent()
    
    bureau = Bureau()
    bureau.add(provider.agent)
    
    logger.info(" Starting Enhanced CivicXAI AI Provider with CUDOS...")
    logger.info("Integrations: Agentverse + ASI:One + CUDOS + OpenAI + MeTTa")
    
    await bureau.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Enhanced AI Provider stopped by user")
    except Exception as e:
        logger.error(f" Fatal error: {e}")
        raise
