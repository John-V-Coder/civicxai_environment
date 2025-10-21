# Frontend-Backend-Cudos Communication Flow - Complete Explanation

## Your Screenshot Issue Explained

**What you're seeing:** When you type "Hi", the AI responds with a generic "I understand you're asking about: 'Hi'" message.

**Why this happens:** Your frontend chat uses **keyword-based intent detection**. It only sends requests to the backend/Gateway/Cudos Cloud when it detects specific keywords. "Hi" doesn't match any keywords, so it returns a canned response locally without ever calling the backend.

---

## Complete System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    USER BROWSER (localhost:5173)                │
│                                                                  │
│  React Components:                                               │
│  ├─ AIGatewayChat.jsx          ← Where you type messages       │
│  ├─ AIGateway.jsx              ← PDF upload forms              │
│  └─ PriorityCalculator.jsx     ← Slider interface              │
│                                                                  │
│  Custom Hooks:                                                   │
│  ├─ useGateway()               ← Gateway API calls             │
│  └─ useMeTTa()                 ← MeTTa API calls               │
│                                                                  │
│  API Client (api.js):                                            │
│  └─ axios instance             ← HTTP client                    │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST with FormData
                              │ URL: http://localhost:8000/api/gateway/*
                              │ Headers: Content-Type: multipart/form-data
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              DJANGO REST API (localhost:8000)                   │
│                                                                  │
│  Gateway Views (gateway_views.py):                              │
│  ├─ GatewayAllocationRequestView                               │
│  │    POST /api/gateway/allocation/request/                     │
│  │    • Receives form data + files from frontend                │
│  │    • Validates data                                          │
│  │    • Forwards to Gateway using httpx                         │
│  │                                                              │
│  ├─ GatewayExplanationRequestView                              │
│  │    POST /api/gateway/explanation/request/                    │
│  │                                                              │
│  ├─ GatewayStatusView                                           │
│  │    GET /api/gateway/status/<request_id>/                     │
│  │    • Frontend polls this to check if request is done         │
│  │                                                              │
│  └─ GatewayHealthView                                           │
│       GET /api/gateway/health/                                   │
│                                                                  │
│  Environment Config:                                             │
│  └─ UAGENTS_GATEWAY_URL = http://localhost:8080                │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ httpx POST
                              │ URL: http://localhost:8080/allocation/request
                              │ Payload: Form data + file contents
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              UAGENTS GATEWAY (localhost:8080)                   │
│                            FastAPI                               │
│                                                                  │
│  Main Functions:                                                 │
│  ├─ Receives allocation/explanation requests                    │
│  ├─ Extracts text from PDFs using PyPDF2                        │
│  ├─ Detects language                                            │
│  ├─ Generates summaries                                         │
│  ├─ Caches processed content (1-hour TTL)                       │
│  └─ Sends to Provider Agent via uagents protocol                │
│                                                                  │
│  Endpoints:                                                      │
│  ├─ POST /allocation/request                                     │
│  ├─ POST /explanation/request                                    │
│  ├─ GET /status/<request_id>                                     │
│  ├─ GET /health                                                  │
│  └─ GET /metrics                                                 │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ uagents messaging protocol
                              │ (Agent-to-Agent communication)
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│          UAGENTS AI PROVIDER (localhost:8002)                   │
│                       uagents runtime                            │
│                                                                  │
│  Provider Agent:                                                 │
│  ├─ Receives allocation data + PDF text from Gateway            │
│  ├─ Formats prompt for AI model                                 │
│  ├─ Calls external AI service:                                  │
│  │   • Option 1: Claude API (Anthropic)                         │
│  │   • Option 2: OpenAI API                                     │
│  │   • Option 3: Cudos Cloud (decentralized compute)            │
│  ├─ Receives AI-generated response                              │
│  └─ Sends response back to Gateway                              │
│                                                                  │
│  Configuration:                                                  │
│  ├─ AI_PROVIDER = "claude" or "openai" or "cudos"              │
│  └─ API keys / Cudos connection details                         │
└────────────────────────────────────────────────────────────────┘
                              │
                              │ (If using Cudos option)
                              │ HTTPS POST
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                      CUDOS CLOUD NETWORK                        │
│                                                                  │
│  Decentralized Compute Infrastructure:                           │
│  ├─ Provides GPU/compute resources                              │
│  ├─ Runs AI models (LLaMA, etc.)                                │
│  ├─ Returns inference results                                    │
│  └─ Handles billing/credits                                      │
│                                                                  │
│  Benefits:                                                       │
│  ├─ Decentralized (no single point of failure)                  │
│  ├─ Cost-effective compute                                       │
│  └─ Scalable AI inference                                        │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example: "Analyze poverty 0.8"

### Step 1: User Input (Frontend)
```javascript
// File: civicxai_frontend/src/components/AIgateway/AIGatewayChat.jsx
// User types: "Analyze poverty 0.8"

const handleSend = async () => {
  // Creates message object
  const userMessage = {
    content: "Analyze poverty 0.8",
    files: []
  };
  
  // Calls processMessage
  await processMessage("Analyze poverty 0.8");
};
```

### Step 2: Intent Detection (Frontend)
```javascript
// File: AIGatewayChat.jsx, line 79-96
const detectIntent = (message) => {
  const lowerMsg = message.toLowerCase();
  
  // "analyze" keyword detected!
  if (lowerMsg.includes('analyze')) {
    return 'analyze';  // ✅ Will trigger backend call
  }
  
  return 'general';  // Would skip backend
};

// Intent = 'analyze' → Proceeds to backend call
```

### Step 3: Extract Metrics & Call Gateway (Frontend)
```javascript
// File: AIGatewayChat.jsx, line 148-191
case 'analyze':
  const analysisMetrics = extractMetrics(userMessage);
  // Result: { poverty_index: 0.8, project_impact: 0.6, ... }
  
  const data = {
    region_id: `CHAT_${Date.now()}`,
    poverty_index: 0.8,
    project_impact: 0.6,
    deforestation: 0.4,
    corruption_risk: 0.3
  };
  
  // Call Gateway hook
  const response = await requestAllocation(data, files);
  // Returns: { request_id: "alloc_abc123" }
```

### Step 4: Gateway Hook Makes HTTP Request (Frontend)
```javascript
// File: civicxai_frontend/src/hooks/useGateway.js, line 21-51
const requestAllocation = async (data, files = []) => {
  // Prepare FormData
  const formData = new FormData();
  formData.append('region_id', data.region_id);
  formData.append('poverty_index', data.poverty_index);
  // ... other fields
  
  // Call API client
  const response = await gatewayAPI.requestAllocation(formData);
  // POST to: http://localhost:8000/api/gateway/allocation/request/
  
  return response.data;
};
```

### Step 5: API Client Sends HTTP Request (Frontend)
```javascript
// File: civicxai_frontend/src/services/api.js, line 159-165
export const gatewayAPI = {
  requestAllocation: (formData) => {
    return publicAPI.post('/gateway/allocation/request/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
};

// Sends to: http://localhost:8000/api/gateway/allocation/request/
```

### Step 6: Django Receives Request (Backend)
```python
# File: civicxai_backend/explainable_ai/gateway_views.py, line 23-143
class GatewayAllocationRequestView(APIView):
    def post(self, request):
        # Parse form data
        form_data = {
            'region_id': request.data.get('region_id'),
            'poverty_index': float(request.data.get('poverty_index', 0)),
            'project_impact': float(request.data.get('project_impact', 0)),
            # ...
        }
        
        # Prepare files
        files = []
        for file_key in request.FILES:
            file_obj = request.FILES[file_key]
            files.append(('files', (file_obj.name, file_obj.read(), ...)))
        
        # Forward to Gateway using httpx
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{GATEWAY_API_URL}/allocation/request",  # Port 8080
                data=form_data,
                files=files
            )
        
        # Return response to frontend
        return Response({
            'request_id': result.get('request_id'),
            'status': 'pending'
        })
```

### Step 7: Gateway Processes Request (Gateway Service)
```python
# File: uagents_gateway/gateway/main.py (conceptual)
@app.post("/allocation/request")
async def allocation_request(
    region_id: str,
    poverty_index: float,
    files: List[UploadFile]
):
    # Extract PDF text
    pdf_text = extract_text_from_pdf(files[0])
    
    # Cache content
    content_cache[region_id] = pdf_text
    
    # Send to Provider Agent via uagents
    await agent.send(
        provider_address,
        AllocationRequest(
            region_id=region_id,
            poverty_index=poverty_index,
            pdf_content=pdf_text
        )
    )
    
    # Return request ID
    return {
        "request_id": f"alloc_{uuid4()}",
        "status": "pending"
    }
```

### Step 8: Provider Calls AI/Cudos (Provider Service)
```python
# File: uagents_ai_provider/providers/main.py (conceptual)
@agent.on_message(AllocationRequest)
async def handle_allocation(ctx: Context, sender: str, msg: AllocationRequest):
    # Format prompt for AI
    prompt = f"""
    Analyze this allocation request:
    Region: {msg.region_id}
    Poverty Index: {msg.poverty_index}
    PDF Content: {msg.pdf_content}
    
    Provide recommendations.
    """
    
    if AI_PROVIDER == "cudos":
        # Call Cudos Cloud
        response = await cudos_client.inference(
            model="llama-3",
            prompt=prompt
        )
    elif AI_PROVIDER == "claude":
        # Call Claude API
        response = anthropic.messages.create(
            model="claude-3-sonnet",
            messages=[{"role": "user", "content": prompt}]
        )
    
    # Send response back to Gateway
    await ctx.send(
        sender,
        AllocationResponse(
            request_id=msg.request_id,
            recommendation=response.text,
            priority_level="high"
        )
    )
```

### Step 9: Frontend Polls for Results
```javascript
// File: civicxai_frontend/src/hooks/useGateway.js, line 104-172
const pollStatus = async (requestId, options = {}) => {
  // Poll every 2 seconds
  const poll = async () => {
    const response = await gatewayAPI.checkStatus(requestId);
    // GET http://localhost:8000/api/gateway/status/alloc_abc123/
    
    if (response.data.status === 'completed') {
      // ✅ Done! Return results
      return response.data.data;
    }
    
    if (response.data.status === 'processing') {
      // ⏳ Wait 2 seconds and try again
      await new Promise(resolve => setTimeout(resolve, 2000));
      return poll();
    }
  };
  
  return poll();
};

// Frontend receives final result:
// {
//   recommendation: {
//     priority_level: "high",
//     confidence_score: 0.85,
//     key_findings: ["High need identified", ...]
//   }
// }
```

### Step 10: Display Results (Frontend)
```javascript
// File: AIGatewayChat.jsx, line 166-176
botResponse = `AI Analysis Complete\n\n` +
  `Priority Level: high\n` +
  `Confidence: 85.0%\n` +
  `Recommended Allocation: 75%\n\n` +
  `Key Findings:\n• High need identified based on poverty index\n...`;

setMessages(prev => [...prev, {
  type: 'bot',
  content: botResponse
}]);
```

---

## Why "Hi" Doesn't Work

```javascript
// User types: "Hi"

// Step 1: detectIntent("Hi")
const lowerMsg = "hi".toLowerCase();

// Step 2: Check keywords
if (lowerMsg.includes('calculate')) { ... }  // ❌ No match
if (lowerMsg.includes('analyze')) { ... }    // ❌ No match
if (lowerMsg.includes('explain')) { ... }    // ❌ No match
if (lowerMsg.includes('health')) { ... }     // ❌ No match

return 'general';  // ✅ Falls through to default

// Step 3: Handle 'general' intent (line 214-221)
default:
  botResponse = `I understand you're asking about: "${userMessage}"\n\n` +
    `To help you better, please be more specific...`;
  
  // ❌ Never calls backend
  // ❌ Never reaches Gateway
  // ❌ Never reaches Cudos Cloud
  
  return botResponse;
```

**Result:** Frontend returns canned response locally. No network request is made.

---

## How to Actually Connect to Backend/Cudos

### Option 1: Use Specific Keywords (Current System)

Type messages with these keywords to trigger backend calls:

```
✅ "Calculate priority for poverty 0.8"    → Calls MeTTa engine
✅ "Analyze this region with high poverty" → Calls Gateway → Cudos
✅ "Explain why this allocation"           → Calls explanation API
✅ "Check health"                          → Checks Gateway status
```

### Option 2: Use the Forms (Not the Chat)

The **Allocation Request** and **Explanation Request** tabs in AIGateway.jsx always send to backend:

```javascript
// File: AIGateway.jsx, line 73-120
const handleAllocationSubmit = async (e) => {
  // ✅ Always calls Gateway, no keyword detection
  const response = await requestAllocation(data, files);
  const finalResult = await pollStatus(response.request_id);
  // Shows results
};
```

### Option 3: Add Free-Form Chat Endpoint (Requires Backend Changes)

To make the chat work like ChatGPT (send all messages to AI), you would need:

1. **New Django endpoint**: `POST /api/gateway/chat/`
2. **New Gateway endpoint**: `POST /chat`
3. **Modified frontend**: Remove intent detection, send everything to backend

---

## Current System Capabilities

### ✅ What Works Now

| Feature | Trigger | Backend Service | Cudos Connection |
|---------|---------|-----------------|------------------|
| Priority calculation | "Calculate priority..." | MeTTa (local) | ❌ No |
| AI analysis | "Analyze..." | Gateway → Provider | ✅ Yes (if configured) |
| Explanation | "Explain..." | MeTTa (local) | ❌ No |
| PDF upload form | Use form tabs | Gateway → Provider | ✅ Yes (if configured) |
| Health check | "Check health" | Gateway | ❌ No |

### ❌ What Doesn't Work

| Input | Why It Fails |
|-------|--------------|
| "Hi" | No matching keyword |
| "Hello" | No matching keyword |
| "What can you do?" | No matching keyword |
| Free-form questions | Intent detection only checks specific keywords |

---

## Cudos Cloud Integration

For requests that use the **"analyze"** keyword or the **Allocation Request form**, here's how Cudos Cloud fits in:

### Provider Configuration
```python
# File: uagents_ai_provider/providers/config.py
AI_PROVIDER = "cudos"  # Options: "claude", "openai", "cudos"

CUDOS_CONFIG = {
    "endpoint": "https://compute.cudos.org/inference",
    "api_key": "your_cudos_api_key",
    "model": "llama-3-70b",
    "max_tokens": 2000
}
```

### When Cudos Is Called
```python
# Provider receives request from Gateway
if AI_PROVIDER == "cudos":
    # Connect to Cudos Cloud
    response = requests.post(
        CUDOS_CONFIG["endpoint"],
        headers={"Authorization": f"Bearer {CUDOS_CONFIG['api_key']}"},
        json={
            "model": CUDOS_CONFIG["model"],
            "prompt": formatted_prompt,
            "max_tokens": CUDOS_CONFIG["max_tokens"]
        }
    )
    
    ai_result = response.json()["choices"][0]["text"]
```

### Flow with Cudos
```
User types "Analyze..." 
  → Frontend detects "analyze" intent
  → Calls Django /gateway/allocation/request/
  → Django forwards to Gateway (port 8080)
  → Gateway extracts PDF text
  → Gateway sends to Provider (port 8002) via uagents
  → Provider checks AI_PROVIDER config
  → If "cudos": Calls Cudos Cloud API
  → Cudos runs inference on decentralized compute
  → Returns result to Provider
  → Provider sends to Gateway
  → Gateway stores result
  → Frontend polls /gateway/status/ until complete
  → Displays result to user
```

---

## Testing the Connection

### 1. Test MeTTa (Local, Fast)
```
Type in chat: "Calculate priority for poverty 0.8"
Expected: Instant response with priority score
```

### 2. Test Gateway (With Provider)
```
Type in chat: "Analyze poverty 0.8 impact 0.9"
Expected: 
  - "Analysis submitted to AI Gateway" toast
  - Polling animation
  - AI-generated response after 2-5 seconds
```

### 3. Test Cudos Connection (If Configured)
```
1. Make sure Provider is configured with AI_PROVIDER="cudos"
2. Type: "Analyze this region with high poverty"
3. Check Provider logs to see Cudos API call
4. Should see Cudos-generated response
```

### 4. Test PDF Upload (Full Stack)
```
1. Go to AI Gateway page
2. Select "Allocation Request" tab
3. Upload a PDF
4. Fill form with region data
5. Click "Submit to AI Gateway"
6. Watch polling status
7. See AI analysis with PDF content incorporated
```

---

## Key Takeaways

1. **Frontend chat uses keyword detection** - Only specific words trigger backend calls
2. **"Hi" is handled locally** - Never reaches backend/Gateway/Cudos
3. **To reach Cudos Cloud**, you must:
   - Use keywords like "analyze" in chat, OR
   - Use the Allocation Request form
   - AND have Provider configured with `AI_PROVIDER="cudos"`
4. **The system has 4 layers**:
   - Frontend (React)
   - Django Backend (API gateway)
   - uAgents Gateway (PDF processing)
   - Provider (AI calls) → Cudos Cloud
5. **Each request is async** - Frontend polls for results
6. **PDFs are processed** at the Gateway layer before sending to AI

---

## Debug Checklist

To verify your full stack is working:

```bash
# 1. Check Django is running
curl http://localhost:8000/api/gateway/health/
# Should return: {"gateway_status": "healthy"}

# 2. Check Gateway is running
curl http://localhost:8080/health
# Should return: {"status": "healthy", "agent_active": true}

# 3. Check Provider is running
# Look for logs showing: "Provider agent started on port 8002"

# 4. Test end-to-end with keyword
# In frontend chat, type: "Analyze poverty 0.8"
# Watch browser Network tab for:
#   - POST to /api/gateway/allocation/request/
#   - Multiple GET to /api/gateway/status/{id}/
```

---

## Summary

Your **current output** shows the chat is working as designed - it's a **keyword-based router**, not a fully conversational AI. To get backend/Cudos responses, use the **specific keywords** or the **form interfaces** that always connect to the backend.

For a true conversational AI experience, you would need to add a new chat endpoint that forwards all messages to the AI, regardless of keywords.
