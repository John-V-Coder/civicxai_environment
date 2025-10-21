# Provider Agent & Cudos Integration Status

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Django API (Port 8000)                        │
│                    gateway_views.py                              │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP POST (PDFs, data)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              Gateway Agent (Port 8080) ✅ ACTIVE                 │
│                                                                   │
│  • Receives HTTP requests from Django                            │
│  • Extracts text from PDFs (PyPDF2)                             │
│  • Processes images with OCR (pytesseract)                      │
│  • Calculates optimization scores                               │
│  • Caches processed content                                     │
└──────────────────────────┬───────────────────────────────────────┘
                           │ uagents messaging
                           │ (includes PDF text, URLs)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│           Provider Agent (Port 8002) ✅ ACTIVE (Simplified)      │
│                                                                   │
│  • Receives: allocation/explanation requests                    │
│  • NOW ACCEPTS: files and urls data (just fixed)                │
│  • Processes: AI analysis via Claude/OpenAI                     │
│  • Returns: recommendations to gateway                           │
│                                                                   │
│  ⚠️  RUNS IN LOCAL MODE (no Almanac registration)               │
│  ⚠️  NO CUDOS INTEGRATION (removed during simplification)       │
└─────────────────────────────────────────────────────────────────┘
                           
                           
┌─────────────────────────────────────────────────────────────────┐
│                Cudos Network ❌ NOT INTEGRATED                   │
│                                                                   │
│  • Decentralized compute network                                │
│  • Would handle distributed AI processing                       │
│  • Would manage resource allocation                             │
│  • Would provide payment/tokenomics                             │
└─────────────────────────────────────────────────────────────────┘
```

## What Works NOW ✅

### 1. **Gateway Agent (Port 8080)**
- ✅ Accepts PDFs via HTTP
- ✅ Extracts text from PDFs
- ✅ Processes images with OCR
- ✅ Fetches URL content
- ✅ Sends data to Provider via uagents

### 2. **Provider Agent (Port 8002)**
- ✅ Receives messages from Gateway
- ✅ **NOW** accepts files and URLs data (just updated)
- ✅ Processes requests with AI (mock or real)
- ✅ Returns recommendations
- ✅ Runs in local mode (no network registration)

### 3. **Django API (Port 8000)**
- ✅ Gateway views for allocation requests
- ✅ Gateway views for explanations
- ✅ Status polling
- ✅ Health checks

## What's Missing ❌

### 1. **Cudos Integration**
The provider was simplified and Cudos integration was removed. The original code had:

```python
# REMOVED CODE (was in original)
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
    
    async def register_compute_provider(self, agent_address: str):
        # Register as compute provider on Cudos network
        pass
    
    async def submit_compute_job(self, job_id: str, job_type: str, data: Dict):
        # Submit compute job to Cudos network
        pass
```

**Why it was removed:**
- Complexity for initial development
- Cudos SDK integration needed
- Network setup requirements
- Focus on core functionality first

### 2. **Advanced AI Processing**
Current provider uses simplified logic:
- Mock responses when no API key
- Basic Claude API calls
- No sophisticated prompt engineering
- Limited error handling

### 3. **Distributed Processing**
- No load balancing across multiple providers
- No fault tolerance
- No job queuing
- Single provider instance

## Data Flow (Current)

### Request with PDF:

1. **Django → Gateway**
   ```python
   # gateway_views.py
   files = [('files', ('report.pdf', pdf_bytes, 'application/pdf'))]
   response = httpx.post(f"{GATEWAY_URL}/allocation/request", data=form_data, files=files)
   ```

2. **Gateway Processes**
   ```python
   # gateway/main.py (line 257-275)
   text = await ContentProcessor.extract_pdf_text(save_path)
   summary = ContentProcessor.summarize_text(text)
   language = ContentProcessor.detect_language_safe(text)
   ```

3. **Gateway → Provider**
   ```python
   # gateway/main.py (line 607-608)
   payload = {
       "files": processed_files,  # Contains extracted text, summaries
       "urls": url_contents,
       "metrics": {...}
   }
   await gateway_agent._ctx.send(AI_PROVIDER_AGENT_ADDRESS, payload)
   ```

4. **Provider Receives** (✅ NOW WORKS)
   ```python
   # providers/main.py (line 48-58)
   class AllocationRequest(Model):
       files: Optional[list] = None  # ✅ Now accepts this
       urls: Optional[list] = None   # ✅ Now accepts this
   ```

5. **Provider Processes**
   ```python
   # providers/main.py (line 104-113)
   if request.files:
       for file in request.files:
           # Uses extracted text in analysis
   ```

6. **Provider → Gateway**
   ```python
   # Response with AI analysis
   await ctx.send(sender, AIResponse(...))
   ```

7. **Django Polls Status**
   ```python
   # gateway_views.py GatewayStatusView
   response = httpx.get(f"{GATEWAY_URL}/status/{request_id}")
   ```

## Current Configuration

### Environment Variables (.env)
```bash
# Provider Configuration
PROVIDER_AGENT_PORT=8002
ANTHROPIC_API_KEY=your_key_here
CHAT_MODEL=claude-3-sonnet-20240229

# Cudos Configuration (NOT USED currently)
CUDOS_NETWORK=testnet
# CUDOS_RPC_ENDPOINT=https://rpc.testnet.cudos.org
# CUDOS_REST_ENDPOINT=https://rest.testnet.cudos.org
```

### Provider Settings (providers/main.py)
```python
# Line 37
CUDOS_NETWORK = os.getenv("CUDOS_NETWORK", "testnet")  # Loaded but not used
```

## How to Add Cudos Integration

If you want full Cudos integration in the future:

### Step 1: Install Cudos SDK
```bash
pip install cudos-sdk  # Or appropriate package
```

### Step 2: Create Cudos Integration Class
```python
class CudosIntegration:
    def __init__(self, network: str, rpc_endpoint: str):
        self.network = network
        self.rpc_endpoint = rpc_endpoint
        self.client = CudosClient(rpc_endpoint)
    
    async def register_provider(self, agent_address: str):
        """Register this agent as compute provider on Cudos network"""
        tx = await self.client.register_compute_provider(
            address=agent_address,
            capabilities=["ai_inference", "text_processing"],
            pricing={"allocation_request": 0.1}  # CUDOS tokens
        )
        return tx
    
    async def submit_job(self, job_id: str, job_type: str, data: dict):
        """Submit compute job to Cudos for distributed processing"""
        tx = await self.client.submit_job(
            job_id=job_id,
            job_type=job_type,
            data=data,
            required_compute=1.0  # Compute units
        )
        return tx
    
    async def get_job_result(self, job_id: str):
        """Retrieve completed job results"""
        result = await self.client.get_job_status(job_id)
        return result
```

### Step 3: Update Provider to Use Cudos
```python
# In main.py
cudos_integration = CudosIntegration(CUDOS_NETWORK, CUDOS_RPC_ENDPOINT)

@provider_protocol.on_message(model=AllocationRequest)
async def handle_allocation_request(ctx: Context, sender: str, msg: AllocationRequest):
    # Submit to Cudos network
    job_id = await cudos_integration.submit_job(
        msg.request_id,
        "allocation_analysis",
        msg.dict()
    )
    
    # Process request
    result = await ai_processor.process_allocation_request(msg)
    
    # Report completion to Cudos
    await cudos_integration.complete_job(job_id, result)
```

### Step 4: Add Payment/Tokenomics
```python
# Check provider balance
balance = await cudos_integration.get_provider_balance()

# Claim rewards for completed jobs
rewards = await cudos_integration.claim_rewards()
```

## Benefits of Cudos Integration

### When Implemented, Would Provide:

1. **Decentralized Compute**
   - Distribute AI processing across multiple nodes
   - Redundancy and fault tolerance
   - Geographic distribution

2. **Token Economics**
   - Get paid in CUDOS tokens for providing compute
   - Pay for AI API calls using token pool
   - Transparent pricing and accounting

3. **Network Effects**
   - Join existing Cudos compute marketplace
   - Access to distributed infrastructure
   - Automatic load balancing

4. **Scalability**
   - Process multiple requests simultaneously
   - Scale horizontally with demand
   - Queue management

## Current Recommendation: Keep It Simple ✅

**For now, the current setup is GOOD because:**

1. ✅ Gateway extracts PDF text (works)
2. ✅ Provider receives files/URLs data (just fixed)
3. ✅ AI processing happens (mock or real API)
4. ✅ Django views handle requests (working)
5. ✅ End-to-end data flow complete

**Add Cudos later when:**
- You need distributed processing
- You want tokenomics
- You require high scalability
- You have multiple provider nodes

## Testing the Current Setup

### Test 1: Send PDF to Gateway
```bash
curl -X POST http://localhost:8080/allocation/request \
  -F "region_id=REG-001" \
  -F "poverty_index=0.85" \
  -F "project_impact=0.90" \
  -F "environmental_score=0.75" \
  -F "corruption_risk=0.30" \
  -F "files=@report.pdf"
```

### Test 2: Django → Gateway → Provider
```python
import requests

response = requests.post(
    'http://localhost:8000/api/gateway/allocation/request/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'},
    data={
        'region_id': 'REG-001',
        'poverty_index': 0.85,
        'project_impact': 0.90,
        'environmental_score': 0.75,
        'corruption_risk': 0.30
    },
    files={'files': open('report.pdf', 'rb')}
)

print(response.json())
# Should see: request_id, status: "pending"

# Poll for results
request_id = response.json()['request_id']
status_response = requests.get(
    f'http://localhost:8000/api/gateway/status/{request_id}/',
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
print(status_response.json())
```

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Gateway Agent | ✅ Working | Processes PDFs, sends to provider |
| Provider Agent | ✅ Working | Now accepts files/URLs, processes AI |
| Django Views | ✅ Working | Complete gateway integration |
| Cudos Integration | ❌ Not Active | Removed for simplicity, can add later |
| PDF Processing | ✅ Working | Gateway extracts, provider receives |
| AI Processing | ⚠️ Simplified | Mock responses or basic API calls |

**Next Steps:**
1. Test the full flow with a PDF
2. Add real Claude API integration
3. Consider Cudos when you need distributed compute
