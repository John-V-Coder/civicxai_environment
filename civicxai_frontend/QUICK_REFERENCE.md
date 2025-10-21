# MeTTa Frontend - Quick Reference

## 🚀 Quick Start

```javascript
import { useMeTTa } from '@/hooks/useMeTTa';

const MyComponent = () => {
  const { calculatePriority, loading } = useMeTTa();
  
  const calc = async () => {
    const result = await calculatePriority({
      poverty_index: 0.85,
      project_impact: 0.90,
      deforestation: 0.75,
      corruption_risk: 0.30
    });
    console.log(result.priority_score); // 0.82
  };
  
  return <button onClick={calc}>Calculate</button>;
};
```

## 📡 API Endpoints

### MeTTa (Fast & Local)
```
POST   /api/metta/calculate-priority/   → Instant score
POST   /api/metta/explain/               → Quick explanation  
GET    /api/metta/health/                → Engine status
```

### Gateway (Advanced & PDFs)
```
POST   /api/gateway/allocation/request/     → Submit with PDFs
POST   /api/gateway/explanation/request/    → Explain with PDFs
GET    /api/gateway/status/<request_id>/    → Poll results
GET    /api/gateway/health/                 → Gateway status
GET    /api/gateway/metrics/                → Performance stats
```

## 🎣 React Hooks

### `useMeTTa()`
```javascript
const { 
  calculatePriority,     // Calculate score
  generateExplanation,   // Get explanation
  checkHealth,           // Health check
  loading,               // Loading state
  error                  // Error state
} = useMeTTa();
```

### `useGateway()`
```javascript
const { 
  requestAllocation,     // Submit with PDFs
  requestExplanation,    // Explain with PDFs
  pollStatus,            // Poll for results
  checkHealth,           // Health check
  getMetrics,            // Get metrics
  loading,               // Submitting state
  polling,               // Polling state
  error                  // Error state
} = useGateway();
```

## 💡 Common Use Cases

### 1. Real-time Calculator
```javascript
const [values, setValues] = useState({...});
const { calculatePriority } = useMeTTa();

useEffect(() => {
  const timer = setTimeout(async () => {
    const result = await calculatePriority(values);
    // Update UI
  }, 500);
  return () => clearTimeout(timer);
}, [values]);
```

### 2. PDF Upload & Analysis
```javascript
const { requestAllocation, pollStatus } = useGateway();

const handleUpload = async (files) => {
  // Submit
  const res = await requestAllocation(data, files);
  
  // Poll
  const result = await pollStatus(res.request_id);
  console.log(result);
};
```

### 3. Generate Explanation
```javascript
const { generateExplanation } = useMeTTa();

const explain = await generateExplanation({
  region_id: 'REG-001',
  allocation_data: { priority_score: 0.85 },
  language: 'en'
});
```

## 📊 Response Formats

### MeTTa Response
```json
{
  "priority_score": 0.82,
  "priority_level": "high",
  "allocation_percentage": 82.0,
  "explanation": "...",
  "processing_time": 0.052
}
```

### Gateway Response
```json
{
  "request_id": "alloc_abc123",
  "status": "completed",
  "data": {
    "priority_level": "high",
    "recommended_allocation_percentage": 75.0,
    "documents_analyzed": 2
  }
}
```

## ⚙️ Configuration

### .env file
```bash
VITE_API_URL=http://localhost:9000/api
```

### Port Setup
- **Django**: 9000 (avoid conflict)
- **Gateway Agent**: 8000
- **Gateway API**: 8080
- **Provider**: 8002

## 🎯 When to Use What

| Need | Use |
|------|-----|
| Instant calculation | `useMeTTa()` |
| PDF analysis | `useGateway()` |
| Real-time slider | `useMeTTa()` |
| AI explanation | Both work |
| Form submission | `useMeTTa()` |
| Document upload | `useGateway()` |

## 🔧 Error Handling
```javascript
const { calculatePriority, error } = useMeTTa();

try {
  await calculatePriority(data);
} catch (err) {
  // Handled automatically
}

// Display in UI
{error && <Alert>{error}</Alert>}
```

## 📁 File Structure
```
src/
├── services/
│   └── api.js              ← API definitions
├── hooks/
│   ├── useMeTTa.js         ← MeTTa hook
│   └── useGateway.js       ← Gateway hook
└── components/
    └── MeTTa/
        └── PriorityCalculator.jsx  ← Example
```

## 🚦 Testing

```javascript
// Test MeTTa connection
import { mettaAPI } from '@/services/api';
mettaAPI.healthCheck().then(console.log);

// Test calculation
mettaAPI.calculatePriority({
  poverty_index: 0.85,
  project_impact: 0.90,
  deforestation: 0.75,
  corruption_risk: 0.30
}).then(console.log);
```

## 📖 Full Documentation
See `METTA_INTEGRATION_GUIDE.md` for complete examples and details.
