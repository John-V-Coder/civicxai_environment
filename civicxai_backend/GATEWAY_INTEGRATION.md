# uAgents Gateway Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Frontend)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST (with PDF files)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST API (Port 8000)                   │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Gateway Views (gateway_views.py)                          │  │
│  │  - GatewayAllocationRequestView                            │  │
│  │  - GatewayExplanationRequestView                           │  │
│  │  - GatewayStatusView                                       │  │
│  │  - GatewayHealthView                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ httpx client                      │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Existing Views (views.py)                                 │  │
│  │  - CalculatePriorityView (MeTTa)                           │  │
│  │  - RegionViewSet (CRUD)                                    │  │
│  │  - AllocationViewSet (CRUD)                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              UAGENTS GATEWAY (Port 8080 - FastAPI)              │
│                                                                   │
│  - Receives PDFs and processes them                             │
│  - Extracts text from PDFs using PyPDF2                         │
│  - Runs optimization calculations                               │
│  - Sends data to Provider Agent via uagents protocol            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uagents messaging
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           UAGENTS AI PROVIDER (Port 8002 - uagents)             │
│                                                                   │
│  - Receives processed data from Gateway                         │
│  - Calls Claude/OpenAI API for AI analysis                      │
│  - Returns recommendations back to Gateway                       │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Submit Allocation Request with PDFs

**Endpoint:** `POST /api/gateway/allocation/request/`

**Purpose:** Send allocation request to uagents gateway with optional PDF uploads

**Request Format:**
```http
POST /api/gateway/allocation/request/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- region_id: "REG-001"
- poverty_index: 0.85
- project_impact: 0.90
- environmental_score: 0.75
- corruption_risk: 0.30
- notes: "Additional context about the region"
- urls: '["https://example.com/data"]'  (JSON string)
- files: [PDF file(s)]
```

**Response:**
```json
{
  "success": true,
  "request_id": "alloc_abc123def456",
  "status": "pending",
  "data": {
    "message": "Allocation request submitted to gateway",
    "priority_score": 0.82,
    "processed_files": 2,
    "processed_urls": 1
  }
}
```

### 2. Request Explanation

**Endpoint:** `POST /api/gateway/explanation/request/`

**Purpose:** Request AI-generated explanation for allocation decisions

**Request Format:**
```http
POST /api/gateway/explanation/request/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- region_id: "REG-001"
- allocation_data: '{"amount": 5000000, "priority": 0.85}'  (JSON string)
- context: "Explain why this region received this allocation"
- language: "en"
- notes: "Focus on poverty factors"
- files: [Supporting PDF documents]
```

**Response:**
```json
{
  "success": true,
  "request_id": "explain_xyz789abc123",
  "status": "pending",
  "data": {
    "message": "Explanation request submitted to gateway",
    "target_language": "en",
    "processed_files": 1
  }
}
```

### 3. Check Request Status

**Endpoint:** `GET /api/gateway/status/<request_id>/`

**Purpose:** Poll for results of a previous request

**Response (Pending):**
```json
{
  "success": true,
  "request_id": "alloc_abc123def456",
  "status": "processing",
  "data": null,
  "timestamp": "2025-10-21T08:30:00Z"
}
```

**Response (Completed):**
```json
{
  "success": true,
  "request_id": "alloc_abc123def456",
  "status": "completed",
  "data": {
    "recommendation": {
      "priority_level": "high",
      "recommended_allocation_percentage": 75.0,
      "confidence_score": 0.85,
      "key_findings": [
        "High need identified based on poverty index",
        "Strong project implementation capacity"
      ],
      "recommendations": [
        {
          "type": "immediate",
          "action": "Allocate resources for infrastructure development"
        }
      ]
    }
  },
  "timestamp": "2025-10-21T08:30:45Z"
}
```

### 4. Check Gateway Health

**Endpoint:** `GET /api/gateway/health/`

**Purpose:** Check if gateway and agents are operational

**Response:**
```json
{
  "success": true,
  "gateway_status": "healthy",
  "agent_active": true,
  "cache_stats": {
    "content_cache_size": 15,
    "url_cache_size": 8
  },
  "timestamp": "2025-10-21T08:30:00Z"
}
```

### 5. Get Gateway Metrics

**Endpoint:** `GET /api/gateway/metrics/`

**Purpose:** Retrieve performance statistics

**Response:**
```json
{
  "success": true,
  "metrics": {
    "total_requests": 45,
    "pending_requests": 3,
    "completed_requests": 42,
    "cache_hit_rate": {
      "content": 0.33,
      "url": 0.16
    }
  }
}
```

## Usage Flow

### Step 1: Submit Request with PDF
```python
import requests

url = "http://localhost:8000/api/gateway/allocation/request/"
headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}

files = {
    'files': ('report.pdf', open('region_report.pdf', 'rb'), 'application/pdf')
}

data = {
    'region_id': 'REG-001',
    'poverty_index': 0.85,
    'project_impact': 0.90,
    'environmental_score': 0.75,
    'corruption_risk': 0.30,
    'notes': 'Region needs urgent infrastructure development'
}

response = requests.post(url, headers=headers, data=data, files=files)
result = response.json()
request_id = result['request_id']
```

### Step 2: Poll for Results
```python
import time

status_url = f"http://localhost:8000/api/gateway/status/{request_id}/"

while True:
    response = requests.get(status_url, headers=headers)
    result = response.json()
    
    if result['status'] == 'completed':
        print("Results:", result['data'])
        break
    elif result['status'] == 'error':
        print("Error:", result['data'])
        break
    
    print("Still processing...")
    time.sleep(2)  # Wait 2 seconds before checking again
```

## Why Use Dedicated Views?

### ✅ Benefits:

1. **Separation of Concerns**
   - Gateway views handle external agent communication
   - MeTTa views handle local AI calculations
   - CRUD ViewSets handle database operations

2. **Maintainability**
   - Easy to locate and modify gateway-specific logic
   - Clear boundaries between different systems
   - Independent testing and debugging

3. **Scalability**
   - Can add more gateway features without touching other code
   - Easy to swap gateway implementation
   - Can add caching, retries, or circuit breakers per view

4. **Error Handling**
   - Gateway-specific error handling (timeouts, connection errors)
   - Different response formats for different concerns
   - Better logging and monitoring per integration point

5. **Security**
   - Can apply different permission classes per integration
   - Separate rate limiting for gateway calls
   - Isolate external API credentials

## Configuration

### Django Settings (settings.py)
```python
# uAgents Gateway Configuration
UAGENTS_GATEWAY_URL = 'http://localhost:8080'
```

### Environment Variables
```bash
# In your .env file
UAGENTS_GATEWAY_URL=http://localhost:8080
```

## PDF Processing

The gateway automatically:
1. Extracts text from PDFs using PyPDF2
2. Detects language of content
3. Generates summaries
4. Caches processed content (1-hour TTL)
5. Sends extracted text to AI provider

**Supported File Types:**
- PDFs (.pdf)
- Images with OCR (.png, .jpg, .jpeg, .bmp, .tiff)
- Text files (.txt, .md, .csv)

## Running the System

### Start Gateway (Port 8080)
```bash
cd uagents_gateway/gateway
python main.py
```

### Start Provider (Port 8002)
```bash
cd uagents_ai_provider/providers
python run_local.py
```

### Start Django API (Port 8000)
```bash
cd civicxai_backend
python manage.py runserver
```

## Testing

### Test Gateway Health
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/gateway/health/
```

### Test Allocation Request
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "region_id=REG-001" \
  -F "poverty_index=0.85" \
  -F "project_impact=0.90" \
  -F "environmental_score=0.75" \
  -F "corruption_risk=0.30" \
  -F "files=@report.pdf" \
  http://localhost:8000/api/gateway/allocation/request/
```

## Troubleshooting

### Gateway Not Reachable
- Check if gateway is running on port 8080
- Verify `UAGENTS_GATEWAY_URL` in settings.py
- Check firewall/network settings

### Request Timeout
- Gateway has 30-second timeout for requests
- Large PDFs may take time to process
- Check gateway logs for processing issues

### Status Returns "processing" Forever
- Provider agent may not be running (port 8002)
- Check provider logs for errors
- Verify agent address configuration

## Architecture Decision Summary

**YES, use dedicated views** because:

1. **Clear separation** between uagents integration and existing MeTTa/CRUD logic
2. **Easier debugging** - know exactly where gateway calls happen
3. **Independent evolution** - can change gateway without affecting other features
4. **Better testing** - can mock gateway responses in tests
5. **Professional architecture** - follows Django/REST best practices
