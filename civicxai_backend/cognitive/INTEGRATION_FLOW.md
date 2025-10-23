# Cognitive-MeTTa-Gateway Integration Flow

## Complete Data Flow: Frontend → Backend → AI Systems → Frontend

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                          │
│  - Dashboard UI                                                   │
│  - Chat Interface                                                 │
│  - Region Analysis Views                                          │
└────────────────┬─────────────────────────────────────────────────┘
                 │ HTTP/REST API
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND (Port 8000)                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              API LAYER (views.py, urls.py)                  ││
│  │  - Gateway Views                                            ││
│  │  - Cognitive Views                                          ││
│  │  - Chat Views                                               ││
│  └───────────────┬─────────────────────────────────────────────┘│
│                  │                                                │
│  ┌───────────────┴───────────────────┬────────────────────────┐ │
│  ▼                                   ▼                        ▼  │
│ ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│ │   METTA      │  │  COGNITIVE   │  │   GATEWAY PROXY     │   │
│ │   ENGINE     │  │   MODULE     │  │  (httpx client)     │   │
│ │              │  │              │  │                     │   │
│ │ - calculate  │  │ - Reasoner   │  │ - Forward to        │   │
│ │ - explain    │  │ - Knowledge  │  │   uAgents Gateway   │   │
│ └──────────────┘  │ - Pipeline   │  └──────────┬──────────┘   │
│                   └──────────────┘             │               │
└────────────────────────────────────────────────┼───────────────┘
                                                  │ HTTP (Port 8001)
                                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              UAGENTS GATEWAY (FastAPI - Port 8001)                │
│                                                                   │
│  - File Processing (PDF, Images)                                 │
│  - URL Content Extraction                                        │
│  - Multi-language Support                                        │
│  - Caching Layer                                                 │
│                                                                   │
│  Endpoints:                                                      │
│  POST /allocation/request                                        │
│  POST /explanation/request                                       │
│  GET  /status/{request_id}                                       │
└────────────────────┬─────────────────────────────────────────────┘
                     │ uAgents Protocol
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ASI AGENT (AI Provider)                        │
│                                                                   │
│  - Advanced AI Analysis                                          │
│  - Natural Language Processing                                   │
│  - Complex Reasoning                                             │
│  - Multi-modal Processing                                        │
│                                                                   │
│  Agent Address: agent1q...                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Examples

### Example 1: Simple Calculation Request

```
1. Frontend → Django
   POST /api/gateway/allocation/request/
   {
     "region_id": "Nairobi",
     "poverty_index": 0.65,
     "project_impact": 0.80,
     ...
   }

2. Django (Gateway View)
   ├─→ Try Gateway (httpx)
   │   └─→ POST http://localhost:8001/allocation/request
   │
   └─→ If Gateway down, Fallback to MeTTa
       └─→ metta_service.calculate_priority()

3. Gateway (if available)
   ├─→ Process request
   ├─→ Send to ASI Agent via uAgents protocol
   └─→ Return request_id

4. Django polls Gateway
   GET /status/{request_id} (every 2 seconds)

5. Gateway returns result
   {
     "status": "completed",
     "data": {
       "priority_score": 0.73,
       "recommendation": "high",
       "ai_analysis": "..."
     }
   }

6. Django → Frontend
   Return combined result with reasoning
```

### Example 2: Cognitive Reasoning Request

```
1. Frontend → Django
   POST /api/cognitive/query/hybrid/
   {
     "query": "What causes poverty in Nairobi?",
     "region_id": "Region_Nairobi",
     "context": {...}
   }

2. Django (Cognitive Orchestrator)
   ├─→ Analyze query complexity
   ├─→ Detect query type: "knowledge_based"
   └─→ Route to: Cognitive Reasoner

3. Cognitive Module
   ├─→ reasoner.reason_about_region("Region_Nairobi", "poverty")
   ├─→ Query AtomSpace knowledge
   ├─→ Apply PLN rules
   ├─→ Build reasoning chain
   └─→ Calculate confidence

4. Return enriched result
   {
     "reasoning_result": {...},
     "confidence": 0.85,
     "reasoning_chain": [...],
     "knowledge_used": true
   }

5. Django → Frontend
   Display reasoning with explanation
```

### Example 3: Hybrid AI Request (Complex)

```
1. Frontend → Django
   POST /api/cognitive/query/hybrid/
   {
     "query": "Analyze Nairobi allocation with uploaded report",
     "region_id": "Region_Nairobi",
     "files": [report.pdf]
   }

2. Django (Hybrid Responder)
   ├─→ Route to ALL systems in parallel
   │
   ├─→ MeTTa: Quick calculation
   │   └─→ priority_score: 0.73
   │
   ├─→ Cognitive: Knowledge reasoning
   │   └─→ reasoning_result: {...}
   │
   └─→ Gateway: Complex AI analysis
       ├─→ Upload PDF to gateway
       ├─→ Gateway processes PDF
       ├─→ Gateway sends to ASI Agent
       └─→ ASI returns comprehensive analysis

3. Hybrid Responder
   ├─→ Combine all results
   ├─→ Weight by confidence
   ├─→ Create unified response
   └─→ Add explanation of sources used

4. Django → Frontend
   {
     "type": "hybrid_response",
     "combined_result": {...},
     "sources": {
       "metta": true,
       "cognitive": true,
       "gateway": true
     },
     "confidence": 0.92
   }
```

---

## API Endpoints

### Django Backend (Port 8000)

#### Cognitive Module Endpoints
```
POST   /api/cognitive/health/              - System health check
POST   /api/cognitive/query/hybrid/        - Intelligent query routing
POST   /api/cognitive/region/analyze/      - Cognitive region analysis
POST   /api/cognitive/ingest/              - Ingest knowledge
POST   /api/cognitive/concept/             - Add concept
GET    /api/cognitive/knowledge/graph/     - Knowledge graph viz
```

#### Gateway Integration Endpoints
```
POST   /api/gateway/allocation/request/    - Send to gateway
POST   /api/gateway/explanation/request/   - Request explanation
GET    /api/gateway/status/{request_id}/   - Poll gateway status
```

#### Chat Endpoints (Uses all systems)
```
POST   /api/chat/message/                  - Intelligent chat
POST   /api/chat/stream/                   - Streaming responses
```

### uAgents Gateway (Port 8001)

```
GET    /                                   - Gateway info
POST   /allocation/request                 - Allocation analysis
POST   /explanation/request                - Explanation generation
GET    /status/{request_id}                - Request status
GET    /health                             - Health check
GET    /metrics                            - System metrics
DELETE /cache/clear                        - Clear caches
```

---

## Integration Points

### 1. Gateway Views (`explainable_ai/views/gateway_views.py`)

**Purpose**: Proxy between Django and uAgents Gateway

```python
class GatewayAllocationRequestView(APIView):
    def post(self, request):
        # Prepare data
        form_data = {...}
        files = [...]
        
        # Try Gateway
        try:
            response = httpx.post(
                f"{GATEWAY_URL}/allocation/request",
                data=form_data,
                files=files
            )
            return Response(response.json())
        
        # Fallback to MeTTa
        except httpx.ConnectError:
            priority = calculate_priority(...)
            return Response({
                "mode": "local_metta",
                "priority_score": priority
            })
```

### 2. Cognitive Integration (NEW - Need to Create)

**File**: `cognitive/integration_views.py`

```python
class HybridQueryView(APIView):
    """Intelligent routing using orchestrator"""
    
    def post(self, request):
        orchestrator = get_orchestrator()
        
        # Analyze query
        routing = orchestrator.analyze_query(query, context)
        
        # Execute based on routing
        if routing['system'] == 'metta':
            result = self._query_metta(...)
        elif routing['system'] == 'cognitive':
            result = self._query_cognitive(...)
        elif routing['system'] == 'gateway':
            result = self._query_gateway(...)
        else:  # hybrid
            result = self._query_hybrid(...)
        
        return Response(result)
```

### 3. MeTTa Service (`metta/metta_service.py`)

**Purpose**: Local MeTTa calculations (fallback)

```python
def calculate_priority(poverty_index, project_impact, 
                      environmental_score, corruption_risk):
    """MeTTa-based priority calculation"""
    metta = MeTTa()
    
    # MeTTa reasoning
    score = (poverty_index * 0.4 + 
             project_impact * 0.3 + 
             environmental_score * 0.2 - 
             corruption_risk * 0.1)
    
    return max(0, min(1, score))
```

### 4. Orchestrator (`cognitive/orchestrator/orchestrator.py`)

**Purpose**: Intelligent query routing

```python
class CognitiveOrchestrator:
    def analyze_query(self, query: str, context: dict):
        """Decide which AI system to use"""
        
        complexity = self._assess_complexity(query)
        has_knowledge = self._check_knowledge_base(query)
        requires_files = context.get('files', [])
        
        if complexity == 'simple' and not has_knowledge:
            return {'system': 'metta', 'confidence': 0.9}
        
        elif has_knowledge and complexity == 'medium':
            return {'system': 'cognitive', 'confidence': 0.85}
        
        elif complexity == 'complex' or requires_files:
            return {'system': 'gateway', 'confidence': 0.8}
        
        else:
            return {'system': 'hybrid', 'confidence': 0.95}
```

---

## Routing Logic

### Decision Tree

```
Query Received
    │
    ├─→ Is it simple math/calculation?
    │   YES → Use MeTTa (fast, local)
    │
    ├─→ Do we have knowledge in AtomSpace?
    │   YES → Use Cognitive Reasoner (knowledge-based)
    │
    ├─→ Does it require file processing?
    │   YES → Use Gateway → ASI Agent (advanced AI)
    │
    ├─→ Is it complex/multi-faceted?
    │   YES → Use Hybrid (combine all systems)
    │
    └─→ Default → Cognitive + Gateway
```

### Query Type Examples

| Query | Routed To | Reason |
|-------|-----------|--------|
| "Calculate priority for region X" | MeTTa | Simple math |
| "What causes poverty in Nairobi?" | Cognitive | Knowledge query |
| "Analyze this PDF report" | Gateway → ASI | File processing |
| "Comprehensive allocation analysis with reasoning" | Hybrid | Complex, multi-system |

---

## Configuration

### Environment Variables

```bash
# .env file
UAGENTS_GATEWAY_URL=http://localhost:8001
AI_PROVIDER_AGENT_ADDRESS=agent1q...
AGENT_NETWORK=testnet

# Optional
COGNITIVE_MODE=hybrid  # metta|cognitive|gateway|hybrid
METTA_FALLBACK_ENABLED=true
GATEWAY_TIMEOUT=60
```

### Django Settings

```python
# settings.py
INSTALLED_APPS = [
    ...
    'cognitive.apps.CognitiveConfig',
    'explainable_ai',
]

# Cognitive settings
COGNITIVE_CONFIG = {
    'orchestrator_enabled': True,
    'hybrid_mode': True,
    'gateway_url': os.getenv('UAGENTS_GATEWAY_URL'),
    'metta_fallback': True,
}
```

---

## Data Flow Patterns

### Pattern 1: Simple Request (MeTTa Only)
```
Frontend → Django → MeTTa → Django → Frontend
Time: ~10ms
```

### Pattern 2: Knowledge Query (Cognitive)
```
Frontend → Django → Cognitive (AtomSpace + PLN) → Django → Frontend
Time: ~100-500ms
```

### Pattern 3: Complex AI (Gateway)
```
Frontend → Django → Gateway → ASI Agent → Gateway → Django → Frontend
Time: ~5-30 seconds (with polling)
```

### Pattern 4: Hybrid (All Systems)
```
Frontend → Django → {
    MeTTa (parallel)
    Cognitive (parallel)
    Gateway → ASI (parallel)
} → Combine → Django → Frontend
Time: ~5-30 seconds (limited by slowest)
```

---

## Implementation Steps

### Step 1: Create Integration Views

Create `cognitive/integration_views.py` with:
- `HybridQueryView`
- `CognitiveRegionAnalysisView`
- `CognitiveKnowledgeIngestView`

### Step 2: Update URLs

```python
# cognitive/urls.py
urlpatterns += [
    path('query/hybrid/', HybridQueryView.as_view()),
    path('region/analyze/', CognitiveRegionAnalysisView.as_view()),
    path('ingest/', CognitiveKnowledgeIngestView.as_view()),
]
```

### Step 3: Update Orchestrator

Enhance `cognitive/orchestrator/orchestrator.py` with:
- Query complexity analysis
- Knowledge base checking
- Routing logic

### Step 4: Test Integration

```bash
# Terminal 1: Start Django
cd civicxai_backend
python manage.py runserver

# Terminal 2: Start Gateway
cd uagents_gateway
python run_uagents.py

# Terminal 3: Test endpoints
curl -X POST http://localhost:8000/api/cognitive/query/hybrid/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze Nairobi", "region_id": "Region_Nairobi"}'
```

---

## Frontend Integration

### React Component Example

```javascript
// CognitiveQuery.jsx
import { useState } from 'react';

function CognitiveQuery() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  
  const handleSubmit = async () => {
    const response = await fetch('/api/cognitive/query/hybrid/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        query: query,
        region_id: 'Region_Nairobi',
        force_mode: 'auto'  // or 'metta', 'cognitive', 'gateway'
      })
    });
    
    const data = await response.json();
    setResult(data);
  };
  
  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleSubmit}>Analyze</button>
      
      {result && (
        <div>
          <h3>Routed to: {result.routing.recommended_system}</h3>
          <p>Confidence: {result.routing.confidence}</p>
          <pre>{JSON.stringify(result.result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

---

## Performance Optimization

### Caching Strategy

```python
# Use Django cache
from django.core.cache import cache

def query_with_cache(query, region_id):
    cache_key = f"cognitive:{region_id}:{hash(query)}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Compute result
    result = execute_query(query, region_id)
    
    # Cache for 1 hour
    cache.set(cache_key, result, 3600)
    
    return result
```

### Async Processing

```python
# Use Celery for long-running tasks
from celery import shared_task

@shared_task
def process_complex_query_async(query, region_id):
    result = gateway_query(query, region_id)
    # Store result in database
    return result
```

---

## System Status Check

```bash
# Check all systems
curl http://localhost:8000/api/cognitive/health/
curl http://localhost:8001/health

# Expected response:
{
  "cognitive": "healthy",
  "atomspace": "active",
  "gateway": "available",
  "metta": "ready",
  "mode": "hybrid"
}
```

---

## Summary

**The integration works as follows:**

1. **Frontend** sends requests to Django REST API
2. **Django** routes requests intelligently:
   - Simple → **MeTTa** (local, fast)
   - Knowledge → **Cognitive** (AtomSpace reasoning)
   - Complex → **Gateway** → **ASI Agent** (advanced AI)
   - Hybrid → **All systems** combined
3. **Results** flow back through Django to Frontend
4. **Fallback** mechanisms ensure system always works

**Key Benefits:**
- Intelligent routing
- Graceful degradation
- Optimal performance
-  Rich AI capabilities
-  Knowledge-based reasoning
