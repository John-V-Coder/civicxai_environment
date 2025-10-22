# 🔄 MeTTa & uAgents Gateway Integration Guide

## Overview

Your CivicXAI system uses a **unified API architecture** where the frontend doesn't need to know about MeTTa or uAgents Gateway URLs. The **Cognitive Orchestrator** automatically routes queries to the appropriate system.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                       │
│              Single Endpoint: /api/chat/                 │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ POST {"message": "..."}
                     ↓
┌──────────────────────────────────────────────────────────┐
│              DJANGO BACKEND (chat_views.py)              │
│         Cognitive Orchestrator Analyzes Query            │
└───┬──────────────┬─────────────┬────────────────────────┘
    │              │             │
    │ Simple       │ Analysis    │ Complex/Documents
    ↓              ↓             ↓
┌────────┐    ┌─────────┐    ┌──────────────┐
│ MeTTa  │    │ Gateway │    │   OpenCog    │
│ Engine │    │ uAgents │    │  Cognitive   │
└────────┘    └─────────┘    └──────────────┘
Local Python   External API    Local Reasoning
```

---

## 🎯 Key Concept: Unified Frontend API

**The frontend ONLY calls ONE endpoint:**

```javascript
// Frontend - Single API call for everything
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userQuery })
});
```

**The backend handles ALL routing automatically!**

---

## ⚙️ Backend Configuration

### 1. Environment Variables (.env)

```env
# MeTTa Engine (Local - Built-in)
# No URL needed - runs as Python module

# uAgents Gateway (External API)
UAGENTS_GATEWAY_URL=http://your-gateway-url:8080

# Optional: Set timeouts
GATEWAY_TIMEOUT=5.0
```

### 2. MeTTa Engine Setup

MeTTa is **built-in** as a Python module. No external URL needed.

**Location:** `civicxai_backend/metta/metta_engine.py`

```python
# Already configured in your system
from metta.metta_engine import metta_engine

# Usage (automatic via orchestrator)
priority_score = metta_engine.calculate_priority(
    poverty_index=0.8,
    project_impact=0.9,
    deforestation=0.4,
    corruption_risk=0.3
)
```

### 3. uAgents Gateway Setup

**External API** - requires configuration.

```python
# In chat_views.py (already configured)
import os
from dotenv import load_dotenv

load_dotenv()
UAGENTS_GATEWAY_URL = os.getenv("UAGENTS_GATEWAY_URL")

# Used automatically when orchestrator routes to Gateway
if UAGENTS_GATEWAY_URL:
    response = httpx.post(f"{UAGENTS_GATEWAY_URL}/analyze", ...)
```

---

## 🔀 Automatic Routing Logic

The **Cognitive Orchestrator** (Phase 4) analyzes each query and routes automatically:

### Routing Rules

```python
# File: cognitive/orchestrator.py

Query Analysis → Routing Decision:

1. Simple calculations → MeTTa
   Examples: "Calculate priority", "Score this region"
   
2. Analysis/Comparison → Gateway (if available)
   Examples: "Analyze region", "Compare two regions"
   
3. Document queries → OpenCog Cognitive
   Examples: "What documents mention poverty?"
   
4. Complex reasoning → OpenCog Cognitive
   Examples: "Explain why...", "Show reasoning..."
   
5. Hybrid needs → MeTTa + Cognitive OR Gateway + Cognitive
   Examples: "Calculate and explain", "Analyze with evidence"
```

---

## 📱 Frontend Integration

### React Component Example

```javascript
// ChatComponent.jsx

import React, { useState } from 'react';

function ChatComponent() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    setLoading(true);
    
    try {
      // SINGLE UNIFIED ENDPOINT
      const res = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: message 
        })
      });
      
      const data = await res.json();
      
      // Response includes:
      // - message: The actual response
      // - intent: Detected intent
      // - routing: Which system handled it (optional)
      
      setResponse(data.message);
      
      // Optional: Show which system was used
      console.log('Handled by:', data.routing || 'auto');
      
    } catch (error) {
      console.error('Error:', error);
      setResponse('Sorry, something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {response && (
          <div className="response">
            {response}
          </div>
        )}
      </div>
      
      <div className="input-area">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask anything..."
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default ChatComponent;
```

---

## 🎭 Query Examples & Routing

### Example 1: Simple Calculation → MeTTa

```javascript
// Frontend
fetch('/api/chat/', {
  body: JSON.stringify({
    message: "Calculate priority for poverty 0.8, impact 0.9"
  })
});

// Backend automatically routes to MeTTa
// Returns: Priority score with calculation details
```

**Backend Flow:**
```
User Query → Orchestrator
           ↓
    "Calculate" detected
           ↓
    Routes to MeTTa
           ↓
    metta_engine.calculate_priority()
           ↓
    Returns result
```

---

### Example 2: Analysis → Gateway (if available)

```javascript
// Frontend
fetch('/api/chat/', {
  body: JSON.stringify({
    message: "Analyze region with poverty 0.7"
  })
});

// Backend routes to Gateway
// If Gateway offline, falls back to local analysis
```

**Backend Flow:**
```
User Query → Orchestrator
           ↓
    "Analyze" detected
           ↓
    Check Gateway availability
           ↓
    If available: httpx.post(UAGENTS_GATEWAY_URL)
    If offline: Local analysis
           ↓
    Returns result
```

---

### Example 3: Document Query → OpenCog

```javascript
// Frontend
fetch('/api/chat/', {
  body: JSON.stringify({
    message: "What documents mention poverty?"
  })
});

// Backend routes to OpenCog Cognitive
// Returns: Documents + reasoning + confidence
```

**Backend Flow:**
```
User Query → Orchestrator
           ↓
    "documents mention" detected
           ↓
    Routes to Cognitive (OpenCog)
           ↓
    knowledge_store.find_sources_for_topic()
           ↓
    Returns documents with reasoning
```

---

### Example 4: Hybrid Query → MeTTa + Cognitive

```javascript
// Frontend
fetch('/api/chat/', {
  body: JSON.stringify({
    message: "Calculate priority and explain why"
  })
});

// Backend uses BOTH systems
// MeTTa for calculation + Cognitive for explanation
```

**Backend Flow:**
```
User Query → Orchestrator
           ↓
    Calculation + Explanation detected
           ↓
    Routes to HYBRID_METTA
           ↓
    1. MeTTa calculates priority
    2. Cognitive explains reasoning
    3. Combines responses
           ↓
    Returns unified result
```

---

## 🛠️ Setup Steps

### Step 1: Backend Configuration

```bash
# 1. Create .env file
cd civicxai_backend
cat > .env << EOF
UAGENTS_GATEWAY_URL=http://your-gateway-url:8080
GATEWAY_TIMEOUT=5.0
EOF

# 2. MeTTa is already built-in (no setup needed)

# 3. Test both systems
python manage.py runserver
```

### Step 2: Test MeTTa Integration

```bash
# Test MeTTa directly
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate priority for poverty 0.8"}'

# Should return priority calculation
```

### Step 3: Test Gateway Integration

```bash
# Test Gateway routing
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze region with poverty 0.7"}'

# Should use Gateway if available
```

### Step 4: Frontend Integration

```javascript
// In your React app
// No special configuration needed!
// Just call /api/chat/ for everything

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const sendMessage = async (message) => {
  const response = await fetch(`${API_URL}/api/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return await response.json();
};
```

---

## 🔍 Checking Which System Was Used

### Backend Logging

The orchestrator logs routing decisions:

```python
# In chat_views.py
print(f"🧠 Cognitive Orchestrator: {routing.value} ({rationale})")

# Console output examples:
# 🧠 Cognitive Orchestrator: metta (Simple calculation - using fast MeTTa engine)
# 🧠 Cognitive Orchestrator: gateway (Analysis required - using uAgents Gateway)
# 🧠 Cognitive Orchestrator: cognitive (Complex reasoning needed - document search)
```

### Frontend Display (Optional)

```javascript
// Show users which system handled their query
const response = await sendMessage(userQuery);

console.log('System used:', response.routing);
// Could display: "Powered by MeTTa", "Analyzed by Gateway", etc.
```

---

## 🎯 Frontend Best Practices

### 1. Single Endpoint Only

```javascript
// ✅ CORRECT - Use unified endpoint
fetch('/api/chat/', { body: JSON.stringify({ message }) })

// ❌ WRONG - Don't call MeTTa/Gateway directly
fetch('/api/metta/calculate/', ...)  // NO!
fetch(GATEWAY_URL, ...)              // NO!
```

### 2. Let Backend Handle Routing

```javascript
// ✅ CORRECT - Send query, let orchestrator decide
const query = "Calculate priority for poverty 0.8";
sendMessage(query);  // Backend routes to MeTTa automatically

// ❌ WRONG - Don't try to route in frontend
if (query.includes('calculate')) {
  callMeTTa(query);  // NO! Backend does this
}
```

### 3. Handle All Response Types

```javascript
const response = await sendMessage(query);

// Response format is consistent regardless of routing
{
  "success": true,
  "message": "...",           // Always present
  "intent": "calculate",      // Optional
  "confidence": 0.85,         // Optional
  "sources": [...],           // Optional (for document queries)
  "reasoning": {...}          // Optional (for explanations)
}
```

---

## 🔧 Fallback Handling

### Gateway Offline

```python
# Backend automatically handles Gateway failures
if UAGENTS_GATEWAY_URL:
    try:
        response = httpx.post(UAGENTS_GATEWAY_URL, timeout=5.0)
    except:
        # Falls back to local analysis
        return self._handle_local_analysis(message)
```

### Frontend Doesn't Need to Handle This

```javascript
// Frontend code stays the same
// Backend handles all fallbacks automatically
const response = await sendMessage(query);
// Works whether Gateway is online or offline
```

---

## 📊 Monitoring Integration

### Check System Status

```bash
# Health check endpoint
curl http://localhost:8000/api/cognitive/health/

# Returns status of all systems:
{
  "status": "healthy",
  "components": {
    "atomspace": "operational",
    "metta": "operational",
    "gateway": "operational",  // or "offline"
    "cognitive": "operational"
  }
}
```

### Get Routing Statistics

```bash
# Learning loop statistics
curl -X POST http://localhost:8000/api/cognitive/learn/ \
  -d '{"operation": "performance"}'

# Returns:
{
  "metta": {
    "total_queries": 150,
    "success_rate": 0.95,
    "average_response_time": 0.08
  },
  "gateway": {
    "total_queries": 75,
    "success_rate": 0.88,
    "average_response_time": 0.45
  },
  "cognitive": {
    "total_queries": 200,
    "success_rate": 0.92,
    "average_response_time": 1.2
  }
}
```

---

## 🚀 Production Deployment

### Environment Variables

```bash
# .env.production
UAGENTS_GATEWAY_URL=https://production-gateway.example.com
GATEWAY_TIMEOUT=10.0

# Optional: Enable/disable systems
ENABLE_METTA=true
ENABLE_GATEWAY=true
ENABLE_COGNITIVE=true
```

### Frontend Environment

```bash
# .env (React)
REACT_APP_API_URL=https://api.civicxai.example.com
```

### CORS Configuration

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://civicxai.example.com",
    "http://localhost:3000",  # Development
]
```

---

## 🎓 Summary

### What You Need to Know:

1. **Frontend calls ONE endpoint:** `/api/chat/`
2. **Backend routes automatically:** Orchestrator decides MeTTa/Gateway/Cognitive
3. **No URL management in frontend:** All URLs configured in backend .env
4. **Fallback is automatic:** If Gateway is offline, system adapts
5. **Consistent response format:** Frontend code works for all routing types

### What Frontend Does:

```javascript
// That's it! Just this:
fetch('/api/chat/', {
  method: 'POST',
  body: JSON.stringify({ message: userQuery })
});
```

### What Backend Does:

```python
# Orchestrator automatically:
1. Analyzes query complexity
2. Detects intent and requirements
3. Routes to best system (MeTTa/Gateway/Cognitive)
4. Handles fallbacks
5. Combines results if needed (Hybrid)
6. Returns unified response
7. Learns from feedback
```

---

## 📞 Quick Reference

| Query Type | Routes To | Response Time | Fallback |
|------------|-----------|---------------|----------|
| "Calculate..." | MeTTa | ~80ms | N/A (local) |
| "Analyze..." | Gateway | ~450ms | Local analysis |
| "What documents..." | Cognitive | ~500ms | N/A (local) |
| "Explain..." | Cognitive | ~1.2s | N/A (local) |
| "Calculate & explain" | Hybrid | ~1.5s | MeTTa only |

---

**Bottom Line:** Your frontend just needs ONE API call to `/api/chat/`. The backend's cognitive orchestrator handles ALL the complexity of routing to MeTTa, Gateway, or OpenCog automatically! 🎉
