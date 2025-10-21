import os
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from contextlib import asynccontextmanager

# Core dependencies
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn
import logging
import shutil
import uuid

# Agent framework
from uagents import Agent, Context, Protocol, Model

# File processing
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

# Text processing
from langdetect import detect, DetectorFactory
from bs4 import BeautifulSoup
import httpx

# Math and optimization
import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import MinMaxScaler

# Async utilities
import aiofiles
from cachetools import TTLCache


load_dotenv()
DetectorFactory.seed = 0  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CivicXAI_Gateway")


GATEWAY_AGENT_SEED = os.getenv("GATEWAY_AGENT_SEED", "civic_xai_gateway_seed")
GATEWAY_AGENT_PORT = int(os.getenv("GATEWAY_AGENT_PORT", 8000))
GATEWAY_AGENT_ENDPOINT = os.getenv(
    "GATEWAY_AGENT_ENDPOINT", 
    f"http://127.0.0.1:{GATEWAY_AGENT_PORT}/submit"
).split(",")

AI_PROVIDER_AGENT_ADDRESS = os.getenv(
    "AI_PROVIDER_AGENT_ADDRESS",
    "agent1qgxrkmld8e70tswvdpznz6zrnmphu9rhuumvjzh2mny8s6he5eq4sdjz27h"
)
AGENT_NETWORK = os.getenv("AGENT_NETWORK", "testnet")
API_PORT = int(os.getenv("API_PORT", 8080))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
CACHE_DIR = os.getenv("CACHE_DIR", "./cache")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024)) 
SUMMARY_RATIO = float(os.getenv("SUMMARY_RATIO", 0.3))


for directory in [UPLOAD_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Thread pool for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

# Cache for processed files and URLs (1 hour TTL)
content_cache = TTLCache(maxsize=100, ttl=3600)
url_cache = TTLCache(maxsize=50, ttl=1800)

# =====================================================
# Mathematical Models & Algorithms
# =====================================================
class AllocationOptimizer:
    """
    Smart allocation optimizer using convex optimization and 
    multi-objective decision making with Pareto efficiency.
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.weights = {
            'poverty': 0.35,
            'impact': 0.30,
            'environment': 0.20,
            'risk': 0.15
        }
    
    def calculate_priority_score(
        self, 
        poverty_index: float,
        project_impact: float,
        environmental_score: float,
        corruption_risk: float
    ) -> Dict[str, float]:
        """
        Calculate multi-dimensional priority score using weighted aggregation
        and risk-adjusted returns.
        
        Formula:
        Priority = w_p·P + w_i·I + w_e·E - w_r·R
        where P=poverty, I=impact, E=environment, R=risk
        
        Returns normalized score and component breakdown.
        """
        # Input validation and normalization
        inputs = np.array([
            poverty_index, 
            project_impact, 
            environmental_score, 
            corruption_risk
        ]).reshape(-1, 1)
        
        # Risk-adjusted calculation
        base_score = (
            self.weights['poverty'] * poverty_index +
            self.weights['impact'] * project_impact +
            self.weights['environment'] * environmental_score -
            self.weights['risk'] * corruption_risk
        )
        
        # Apply sigmoid for smooth scaling
        normalized_score = 1 / (1 + np.exp(-5 * (base_score - 0.5)))
        
        # Calculate confidence intervals using bootstrap method
        confidence = self._calculate_confidence(inputs)
        
        return {
            'priority_score': float(normalized_score),
            'base_score': float(base_score),
            'confidence_interval': confidence,
            'risk_adjusted_return': float(base_score / (1 + corruption_risk)),
            'components': {
                'poverty_contribution': self.weights['poverty'] * poverty_index,
                'impact_contribution': self.weights['impact'] * project_impact,
                'environment_contribution': self.weights['environment'] * environmental_score,
                'risk_penalty': self.weights['risk'] * corruption_risk
            }
        }
    
    def _calculate_confidence(self, inputs: np.ndarray, n_bootstrap: int = 100) -> Tuple[float, float]:
        """Calculate 95% confidence interval using bootstrap resampling."""
        bootstrap_scores = []
        for _ in range(n_bootstrap):
            sampled = inputs + np.random.normal(0, 0.05, inputs.shape)
            sampled = np.clip(sampled, 0, 1)
            score = np.mean(sampled)
            bootstrap_scores.append(score)
        
        return (
            float(np.percentile(bootstrap_scores, 2.5)),
            float(np.percentile(bootstrap_scores, 97.5))
        )
    
    def optimize_allocation(
        self, 
        regions: List[Dict[str, float]], 
        total_budget: float
    ) -> List[Dict[str, Any]]:
        """
        Optimize budget allocation across multiple regions using 
        constrained optimization with fairness constraints.
        
        Solves: maximize Σ(score_i · allocation_i)
        subject to: Σ allocation_i = total_budget
                    allocation_i ≥ min_allocation
        """
        n = len(regions)
        scores = np.array([r['priority_score'] for r in regions])
        
        # Objective: maximize weighted allocation
        def objective(x):
            return -np.sum(scores * x)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget},
            {'type': 'ineq', 'fun': lambda x: x - 0.05 * total_budget}  # Min 5% each
        ]
        
        # Initial guess: proportional to scores
        x0 = scores / np.sum(scores) * total_budget
        
        # Bounds: 0 to total_budget
        bounds = [(0, total_budget) for _ in range(n)]
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        allocations = []
        for i, region in enumerate(regions):
            allocations.append({
                **region,
                'allocated_budget': float(result.x[i]),
                'allocation_percentage': float(result.x[i] / total_budget * 100)
            })
        
        return allocations

# =====================================================
# Pydantic Models
# =====================================================
class AllocationRequestInput(BaseModel):
    region_id: str
    poverty_index: float = Field(ge=0, le=1, description="Poverty index (0-1)")
    project_impact: float = Field(ge=0, le=1, description="Expected project impact")
    environmental_score: float = Field(ge=0, le=1, description="Environmental sustainability score")
    corruption_risk: float = Field(ge=0, le=1, description="Corruption risk factor")
    notes: Optional[str] = Field(None, description="Additional context and notes")
    urls: Optional[List[str]] = Field(None, description="Reference URLs")
    
    @validator('urls')
    def validate_urls(cls, v):
        if v:
            for url in v:
                if not url.startswith(('http://', 'https://')):
                    raise ValueError(f"Invalid URL: {url}")
        return v

class ExplanationRequestInput(BaseModel):
    region_id: str
    allocation_data: Dict[str, Any]
    context: str = ""
    language: str = "en"
    urls: Optional[List[str]] = None
    notes: Optional[str] = None

class RequestStatusResponse(BaseModel):
    request_id: str
    status: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# =====================================================
# Content Processing Pipeline
# =====================================================
class ContentProcessor:
    """Unified content processing pipeline with caching and optimization."""
    
    @staticmethod
    def generate_cache_key(content: str) -> str:
        """Generate cache key from content hash."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    async def extract_pdf_text(file_path: str) -> str:
        """Extract text from PDF asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            ContentProcessor._sync_extract_pdf,
            file_path
        )
    
    @staticmethod
    def _sync_extract_pdf(file_path: str) -> str:
        """Synchronous PDF text extraction."""
        try:
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return f"[Error extracting PDF: {e}]"
    
    @staticmethod
    async def extract_image_text(file_path: str) -> str:
        """Extract text from image using OCR asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            ContentProcessor._sync_extract_image,
            file_path
        )
    
    @staticmethod
    def _sync_extract_image(file_path: str) -> str:
        """Synchronous image OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return f"[Error processing image: {e}]"
    
    @staticmethod
    def summarize_text(text: str, ratio: float = SUMMARY_RATIO) -> str:
        """
        Smart text summarization using extractive method.
        Falls back to truncation if text is too short.
        """
        if not text or len(text) < 200:
            return text
        
        # Simple extractive summarization: keep most informative sentences
        sentences = text.split('.')
        if len(sentences) <= 5:
            return text
        
        # Keep first, last, and middle sentences for context
        keep_count = max(3, int(len(sentences) * ratio))
        indices = [0, len(sentences)//2, len(sentences)-1]
        
        # Add more sentences if needed
        step = len(sentences) // keep_count
        indices.extend(range(step, len(sentences), step))
        indices = sorted(set(indices))[:keep_count]
        
        summary = '. '.join([sentences[i] for i in indices if i < len(sentences)])
        return summary + '.'
    
    @staticmethod
    def detect_language_safe(text: str) -> str:
        """Safely detect language with fallback."""
        try:
            if not text or len(text) < 10:
                return "unknown"
            return detect(text)
        except:
            return "unknown"
    
    @staticmethod
    async def process_file(file: UploadFile) -> Dict[str, Any]:
        """
        Process uploaded file: extract text, detect language, summarize.
        Uses caching to avoid reprocessing identical files.
        """
        try:
            # Save file temporarily
            ext = os.path.splitext(file.filename)[-1].lower()
            unique_name = f"{uuid.uuid4()}{ext}"
            save_path = os.path.join(UPLOAD_DIR, unique_name)
            
            async with aiofiles.open(save_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Check cache
            cache_key = ContentProcessor.generate_cache_key(str(content))
            if cache_key in content_cache:
                logger.info(f"Cache hit for file: {file.filename}")
                return content_cache[cache_key]
            
            # Extract text based on file type
            if ext == '.pdf':
                text = await ContentProcessor.extract_pdf_text(save_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                text = await ContentProcessor.extract_image_text(save_path)
            elif ext in ['.txt', '.md', '.csv']:
                async with aiofiles.open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = await f.read()
            else:
                text = f"[Unsupported file type: {ext}]"
            
            # Process text
            language = ContentProcessor.detect_language_safe(text)
            summary = ContentProcessor.summarize_text(text)
            
            result = {
                "filename": file.filename,
                "content": text,
                "summary": summary,
                "language": language,
                "size": len(text),
                "processed_at": datetime.now().isoformat()
            }
            
            # Cache result
            content_cache[cache_key] = result
            
            # Cleanup
            os.remove(save_path)
            
            return result
            
        except Exception as e:
            logger.error(f"File processing error for {file.filename}: {e}")
            return {
                "filename": file.filename,
                "content": f"[Error: {e}]",
                "summary": "",
                "language": "unknown",
                "size": 0,
                "processed_at": datetime.now().isoformat()
            }
    
    @staticmethod
    async def fetch_url_content(url: str) -> Dict[str, str]:
        """Fetch and extract text from URL with caching."""
        # Check cache
        if url in url_cache:
            logger.info(f"Cache hit for URL: {url}")
            return url_cache[url]
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                
                # Remove scripts, styles, and non-content elements
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                
                # Extract visible text
                text = soup.get_text(separator="\n")
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                content = "\n".join(lines)
                
                language = ContentProcessor.detect_language_safe(content)
                summary = ContentProcessor.summarize_text(content)
                
                result = {
                    "url": url,
                    "content": content,
                    "summary": summary,
                    "language": language,
                    "fetched_at": datetime.now().isoformat()
                }
                
                # Cache result
                url_cache[url] = result
                
                return result
                
        except Exception as e:
            logger.error(f"URL fetch error for {url}: {e}")
            return {
                "url": url,
                "content": f"[Error fetching URL: {e}]",
                "summary": "",
                "language": "unknown",
                "fetched_at": datetime.now().isoformat()
            }

# =====================================================
# Gateway Agent Setup
# =====================================================
gateway_agent: Optional[Agent] = None
gateway_protocol: Optional[Protocol] = None
pending_requests: Dict[str, Dict[str, Any]] = {}
optimizer = AllocationOptimizer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global gateway_agent, gateway_protocol, pending_requests
    
    # Initialize agent
    gateway_agent = Agent(
        name="CivicXAI_Gateway",
        seed=GATEWAY_AGENT_SEED,
        port=GATEWAY_AGENT_PORT,
        endpoint=GATEWAY_AGENT_ENDPOINT
    )
    
    pending_requests = {}
    gateway_protocol = Protocol(name="CivicXAI_Gateway_Protocol", version="2.0.0")
    
    @gateway_protocol.on_message(model=Model)
    async def handle_response(ctx: Context, sender: str, msg: Model):
        """Handle responses from AI provider."""
        if hasattr(msg, "request_id"):
            request_id = msg.request_id
            pending_requests[request_id] = {
                "status": "completed",
                "data": msg.dict(),
                "completed_at": datetime.now().isoformat()
            }
            logger.info(f"Response received for request: {request_id}")
    
    gateway_agent.include(gateway_protocol, publish_manifest=True)
    asyncio.create_task(gateway_agent.run_async())
    
    logger.info(f"🚀 Gateway agent started: {gateway_agent.address}")
    logger.info(f"📡 Network: {AGENT_NETWORK}")
    logger.info(f"🔌 Port: {GATEWAY_AGENT_PORT}")
    
    yield
    
    logger.info("🛑 Shutting down gateway...")

# =====================================================
# FastAPI Application
# =====================================================
app = FastAPI(
    title="CivicXAI Gateway API",
    version="2.0.0",
    description="Advanced AI-powered civic resource allocation gateway",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =====================================================
#  API Endpoints
# =====================================================
@app.get("/")
async def root():
    """API root endpoint with system information."""
    return {
        "service": "CivicXAI Gateway",
        "version": "2.0.0",
        "status": "running",
        "network": AGENT_NETWORK,
        "agent_address": gateway_agent.address if gateway_agent else None,
        "features": [
            "Multi-format file processing (PDF, images, text)",
            "URL content extraction",
            "Mathematical optimization",
            "Smart caching",
            "Async processing",
            "Language detection",
            "Text summarization"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/allocation/request", response_model=RequestStatusResponse)
async def request_allocation(
    background_tasks: BackgroundTasks,
    region_id: str = Form(...),
    poverty_index: float = Form(..., ge=0, le=1),
    project_impact: float = Form(..., ge=0, le=1),
    environmental_score: float = Form(..., ge=0, le=1),
    corruption_risk: float = Form(..., ge=0, le=1),
    notes: Optional[str] = Form(None),
    urls: Optional[str] = Form(None),  # JSON string of URLs
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Request resource allocation with optimization.
    Supports files, URLs, and complex text inputs.
    """
    try:
        request_id = f"alloc_{uuid.uuid4().hex[:12]}"
        pending_requests[request_id] = {"status": "processing"}
        
        # Parse URLs if provided
        url_list = json.loads(urls) if urls else []
        
        # Process files asynchronously
        processed_files = []
        if files:
            file_tasks = [ContentProcessor.process_file(f) for f in files]
            processed_files = await asyncio.gather(*file_tasks)
        
        # Fetch URL contents asynchronously
        url_contents = []
        if url_list:
            url_tasks = [ContentProcessor.fetch_url_content(url) for url in url_list]
            url_contents = await asyncio.gather(*url_tasks)
        
        # Calculate priority score
        optimization_result = optimizer.calculate_priority_score(
            poverty_index,
            project_impact,
            environmental_score,
            corruption_risk
        )
        
        # Detect language from notes
        notes_language = ContentProcessor.detect_language_safe(notes) if notes else "unknown"
        
        # Prepare payload
        payload = {
            "request_id": request_id,
            "type": "allocation_request",
            "region_id": region_id,
            "metrics": {
                "poverty_index": poverty_index,
                "project_impact": project_impact,
                "environmental_score": environmental_score,
                "corruption_risk": corruption_risk
            },
            "optimization": optimization_result,
            "notes": {
                "content": notes,
                "language": notes_language
            } if notes else None,
            "files": processed_files if processed_files else None,
            "urls": url_contents if url_contents else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to AI provider
        if gateway_agent and gateway_agent._ctx:
            await gateway_agent._ctx.send(AI_PROVIDER_AGENT_ADDRESS, payload)
            logger.info(f"Allocation request sent: {request_id}")
        
        return RequestStatusResponse(
            request_id=request_id,
            status="pending",
            data={
                "message": "Allocation request submitted successfully",
                "priority_score": optimization_result['priority_score'],
                "processed_files": len(processed_files),
                "processed_urls": len(url_contents)
            }
        )
        
    except Exception as e:
        logger.error(f"Allocation request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explanation/request", response_model=RequestStatusResponse)
async def request_explanation(
    background_tasks: BackgroundTasks,
    region_id: str = Form(...),
    allocation_data: str = Form(...),  # JSON string
    context: str = Form(""),
    language: str = Form("en"),
    urls: Optional[str] = Form(None),  # JSON string
    notes: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Request explanation for allocation decision.
    Supports multi-language and comprehensive context.
    """
    try:
        request_id = f"explain_{uuid.uuid4().hex[:12]}"
        pending_requests[request_id] = {"status": "processing"}
        
        # Parse inputs
        url_list = json.loads(urls) if urls else []
        allocation_dict = json.loads(allocation_data)
        
        # Process files
        processed_files = []
        if files:
            file_tasks = [ContentProcessor.process_file(f) for f in files]
            processed_files = await asyncio.gather(*file_tasks)
        
        # Fetch URLs
        url_contents = []
        if url_list:
            url_tasks = [ContentProcessor.fetch_url_content(url) for url in url_list]
            url_contents = await asyncio.gather(*url_tasks)
        
        # Detect notes language
        notes_language = ContentProcessor.detect_language_safe(notes) if notes else language
        
        # Prepare payload
        payload = {
            "request_id": request_id,
            "type": "explanation_request",
            "region_id": region_id,
            "allocation_data": allocation_dict,
            "context": context,
            "language": language,
            "notes": {
                "content": notes,
                "language": notes_language
            } if notes else None,
            "files": processed_files if processed_files else None,
            "urls": url_contents if url_contents else None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to AI provider
        if gateway_agent and gateway_agent._ctx:
            await gateway_agent._ctx.send(AI_PROVIDER_AGENT_ADDRESS, payload)
            logger.info(f"Explanation request sent: {request_id}")
        
        return RequestStatusResponse(
            request_id=request_id,
            status="pending",
            data={
                "message": "Explanation request submitted successfully",
                "target_language": language,
                "processed_files": len(processed_files),
                "processed_urls": len(url_contents)
            }
        )
        
    except Exception as e:
        logger.error(f"Explanation request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{request_id}", response_model=RequestStatusResponse)
async def get_request_status(request_id: str):
    """Check status of a request."""
    if request_id not in pending_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request_data = pending_requests[request_id]
    status = request_data.get("status", "unknown")
    
    return RequestStatusResponse(
        request_id=request_id,
        status=status,
        data=request_data.get("data") if status == "completed" else None
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_active": gateway_agent is not None,
        "cache_stats": {
            "content_cache_size": len(content_cache),
            "url_cache_size": len(url_cache)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics and statistics."""
    return {
        "total_requests": len(pending_requests),
        "pending_requests": sum(1 for r in pending_requests.values() if r.get("status") == "processing"),
        "completed_requests": sum(1 for r in pending_requests.values() if r.get("status") == "completed"),
        "cache_hit_rate": {
            "content": len(content_cache) / max(1, len(pending_requests)),
            "url": len(url_cache) / max(1, len(pending_requests))
        },
        "uptime": datetime.now().isoformat(),
        "system": {
            "upload_dir": UPLOAD_DIR,
            "max_file_size": MAX_FILE_SIZE,
            "cache_ttl": "3600s"
        }
    }

@app.delete("/cache/clear")
async def clear_cache():
    """Clear all caches (admin endpoint)."""
    content_cache.clear()
    url_cache.clear()
    logger.info("All caches cleared")
    return {"message": "Caches cleared successfully"}

# =====================================================
# Application Entry Point
# =====================================================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=False,
        log_level="info",
        access_log=True
    )