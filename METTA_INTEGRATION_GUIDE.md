# MeTTa Frontend Integration Guide

## Overview

This guide shows how to use the **MeTTa AI engine** and **Gateway (uagents)** in your React frontend.

## Quick Start

### 1. Import the Hooks

```javascript
import { useMeTTa } from '@/hooks/useMeTTa';
import { useGateway } from '@/hooks/useGateway';
```

### 2. Use in Components

```javascript
const MyComponent = () => {
  const { calculatePriority, loading } = useMeTTa();
  
  const handleCalculate = async () => {
    const result = await calculatePriority({
      poverty_index: 0.85,
      project_impact: 0.90,
      deforestation: 0.75,
      corruption_risk: 0.30
    });
    
    console.log(result.priority_score);
  };
  
  return <button onClick={handleCalculate}>Calculate</button>;
};
```

## API Services

### MeTTa API (`mettaAPI`)

Fast, local AI calculations without PDFs.

```javascript
import { mettaAPI } from '@/services/api';

// Calculate priority (instant)
const result = await mettaAPI.calculatePriority({
  poverty_index: 0.85,
  project_impact: 0.90,
  deforestation: 0.75,
  corruption_risk: 0.30
});

// Generate explanation
const explanation = await mettaAPI.generateExplanation({
  region_id: 'REG-001',
  allocation_data: { priority_score: 0.85 },
  language: 'en'
});

// Health check
const health = await mettaAPI.healthCheck();
```

### Gateway API (`gatewayAPI`)

Advanced AI with PDF support (async processing).

```javascript
import { gatewayAPI } from '@/services/api';

// Submit allocation request with PDFs
const formData = new FormData();
formData.append('region_id', 'REG-001');
formData.append('poverty_index', 0.85);
formData.append('files', pdfFile);

const response = await gatewayAPI.requestAllocation(formData);
const requestId = response.request_id;

// Poll for results
const result = await gatewayAPI.checkStatus(requestId);
```

## React Hooks

### `useMeTTa()` Hook

For fast, local calculations.

```javascript
import { useMeTTa } from '@/hooks/useMeTTa';

const MyComponent = () => {
  const { 
    calculatePriority, 
    generateExplanation, 
    checkHealth,
    loading, 
    error 
  } = useMeTTa();

  // Calculate priority
  const handleCalc = async () => {
    const result = await calculatePriority({
      poverty_index: 0.85,
      project_impact: 0.90,
      deforestation: 0.75,
      corruption_risk: 0.30
    });
    
    console.log('Priority:', result.priority_score);
    console.log('Level:', result.priority_level);
  };

  // Generate explanation
  const handleExplain = async () => {
    const result = await generateExplanation({
      region_id: 'REG-001',
      allocation_data: { priority_score: 0.85 },
      language: 'en'
    });
    
    console.log('Explanation:', result.explanation);
  };

  return (
    <div>
      <button onClick={handleCalc} disabled={loading}>
        Calculate
      </button>
      {error && <p>{error}</p>}
    </div>
  );
};
```

### `useGateway()` Hook

For advanced AI with PDFs (async with polling).

```javascript
import { useGateway } from '@/hooks/useGateway';

const MyComponent = () => {
  const { 
    requestAllocation, 
    pollStatus,
    loading, 
    polling,
    error 
  } = useGateway();

  const [result, setResult] = useState(null);

  const handleSubmit = async (files) => {
    // Submit request
    const response = await requestAllocation({
      region_id: 'REG-001',
      poverty_index: 0.85,
      project_impact: 0.90,
      environmental_score: 0.75,
      corruption_risk: 0.30
    }, files);

    // Poll for results
    const finalResult = await pollStatus(response.request_id, {
      maxAttempts: 30,
      interval: 2000,
      onUpdate: (status) => {
        console.log('Status:', status.status);
      }
    });

    setResult(finalResult);
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={(e) => handleSubmit([e.target.files[0]])} 
      />
      {polling && <p>Processing...</p>}
      {result && <div>{JSON.stringify(result)}</div>}
    </div>
  );
};
```

## Complete Examples

### Example 1: Simple Priority Calculator

```javascript
import React, { useState } from 'react';
import { useMeTTa } from '@/hooks/useMeTTa';

const SimplePriorityCalc = () => {
  const { calculatePriority, loading } = useMeTTa();
  const [score, setScore] = useState(null);

  const handleCalc = async () => {
    const result = await calculatePriority({
      poverty_index: 0.85,
      project_impact: 0.90,
      deforestation: 0.75,
      corruption_risk: 0.30
    });
    setScore(result.priority_score);
  };

  return (
    <div>
      <button onClick={handleCalc} disabled={loading}>
        {loading ? 'Calculating...' : 'Calculate'}
      </button>
      {score && <h2>Score: {(score * 100).toFixed(1)}%</h2>}
    </div>
  );
};
```

### Example 2: Real-time Slider Calculator

```javascript
import React, { useState, useEffect } from 'react';
import { useMeTTa } from '@/hooks/useMeTTa';
import { Slider } from '@/components/ui/slider';

const RealtimeCalculator = () => {
  const { calculatePriority } = useMeTTa();
  const [values, setValues] = useState({
    poverty_index: 0.5,
    project_impact: 0.5,
    deforestation: 0.5,
    corruption_risk: 0.3
  });
  const [result, setResult] = useState(null);

  // Auto-calculate on value change (debounced)
  useEffect(() => {
    const timer = setTimeout(async () => {
      const res = await calculatePriority(values);
      setResult(res);
    }, 500);

    return () => clearTimeout(timer);
  }, [values]);

  return (
    <div>
      <Slider
        value={[values.poverty_index]}
        onValueChange={([v]) => setValues({...values, poverty_index: v})}
        min={0}
        max={1}
        step={0.01}
      />
      {result && <p>Priority: {result.priority_level}</p>}
    </div>
  );
};
```

### Example 3: PDF Upload with Gateway

```javascript
import React, { useState } from 'react';
import { useGateway } from '@/hooks/useGateway';

const PDFUploader = () => {
  const { requestAllocation, pollStatus, loading, polling } = useGateway();
  const [result, setResult] = useState(null);
  const [files, setFiles] = useState([]);

  const handleSubmit = async () => {
    // Submit with PDFs
    const response = await requestAllocation({
      region_id: 'REG-001',
      poverty_index: 0.85,
      project_impact: 0.90,
      environmental_score: 0.75,
      corruption_risk: 0.30,
      notes: 'Region needs urgent support'
    }, files);

    console.log('Request submitted:', response.request_id);

    // Poll for results
    const finalResult = await pollStatus(response.request_id, {
      onUpdate: (status) => {
        console.log('Current status:', status.status);
      }
    });

    setResult(finalResult);
  };

  return (
    <div>
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />
      <button onClick={handleSubmit} disabled={loading || polling}>
        {loading && 'Submitting...'}
        {polling && 'Processing...'}
        {!loading && !polling && 'Submit'}
      </button>
      {result && (
        <div>
          <h3>Results:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
```

### Example 4: Explanation Generator

```javascript
import React, { useState } from 'react';
import { useMeTTa } from '@/hooks/useMeTTa';

const ExplanationGenerator = ({ regionId, allocationData }) => {
  const { generateExplanation, loading } = useMeTTa();
  const [explanation, setExplanation] = useState(null);

  const handleGenerate = async () => {
    const result = await generateExplanation({
      region_id: regionId,
      allocation_data: allocationData,
      language: 'en'
    });
    setExplanation(result.explanation);
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        Explain Decision
      </button>
      {explanation && (
        <div className="explanation">
          <p>{explanation}</p>
        </div>
      )}
    </div>
  );
};
```

## When to Use What

### Use **MeTTa** (`useMeTTa`) when:
- ✅ You need **instant** calculations
- ✅ Simple form inputs (no PDFs)
- ✅ Real-time UI updates
- ✅ Interactive sliders/calculators
- ✅ Quick priority checks

### Use **Gateway** (`useGateway`) when:
- ✅ You have **PDF documents** to analyze
- ✅ Need AI-powered explanations
- ✅ Complex analysis required
- ✅ External data references (URLs)
- ✅ Advanced recommendations

## API Response Formats

### MeTTa Response:
```json
{
  "priority_score": 0.82,
  "priority_level": "high",
  "allocation_percentage": 82.0,
  "factors": {
    "poverty_index": 0.34,
    "project_impact": 0.27,
    "deforestation": 0.15,
    "corruption_risk": -0.03
  },
  "explanation": "High priority due to poverty and impact...",
  "processing_time": 0.052
}
```

### Gateway Response (after polling):
```json
{
  "request_id": "alloc_abc123",
  "status": "completed",
  "data": {
    "priority_level": "high",
    "recommended_allocation_percentage": 75.0,
    "confidence_score": 0.85,
    "key_findings": [...],
    "recommendations": [...],
    "documents_analyzed": 2,
    "urls_analyzed": 1
  }
}
```

## Environment Configuration

Update your `.env` file:

```bash
# Django API URL (update if Django runs on different port)
VITE_API_URL=http://localhost:9000/api
```

If Django runs on port 8000 (conflicts with gateway agent), change it:

```bash
# Run Django on different port
python manage.py runserver 9000

# Update .env
VITE_API_URL=http://localhost:9000/api
```

## Error Handling

All hooks provide error handling:

```javascript
const { calculatePriority, error } = useMeTTa();

try {
  const result = await calculatePriority(data);
} catch (err) {
  // Error already set in hook's error state
  // Also shown via toast notification
  console.error(err);
}

// Display error in UI
{error && <Alert variant="destructive">{error}</Alert>}
```

## Loading States

Manage loading states for better UX:

```javascript
const { calculatePriority, loading } = useMeTTa();

<button disabled={loading}>
  {loading ? (
    <>
      <Loader2 className="animate-spin" />
      Calculating...
    </>
  ) : (
    'Calculate'
  )}
</button>
```

## Integration Checklist

- ✅ API endpoints configured (`mettaAPI`, `gatewayAPI`)
- ✅ React hooks created (`useMeTTa`, `useGateway`)
- ✅ Example component (PriorityCalculator)
- ✅ Environment variables set (`.env`)
- ✅ Django running on port 9000
- ✅ Gateway running on port 8080
- ✅ Provider running on port 8002

## Next Steps

1. **Add to your routes:**
```javascript
import PriorityCalculator from '@/components/MeTTa/PriorityCalculator';

// In your router
<Route path="/calculator" element={<PriorityCalculator />} />
```

2. **Use in existing components:**
```javascript
import { useMeTTa } from '@/hooks/useMeTTa';

// In your region detail page
const { calculatePriority } = useMeTTa();
```

3. **Test the connection:**
```javascript
// Quick test in browser console
import { mettaAPI } from '@/services/api';
mettaAPI.healthCheck().then(console.log);
```

## Summary

You now have:
- ✅ **MeTTa API** - Fast local calculations
- ✅ **Gateway API** - Advanced AI with PDFs
- ✅ **React Hooks** - Easy component integration
- ✅ **Example Components** - Working reference code
- ✅ **Complete Documentation** - This guide

Start using MeTTa in your frontend today! 🚀
