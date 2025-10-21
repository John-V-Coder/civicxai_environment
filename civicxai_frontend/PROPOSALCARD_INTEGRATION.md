# 🎯 ProposalCard Integration Guide

## Overview

The enhanced `ProposalCard` component is now fully integrated with:
- ✅ **useGateway** hook - Advanced AI analysis with uAgents
- ✅ **useMeTTa** hook - Fast local priority calculations
- ✅ **proposalsAPI** - Backend API integration

## 📦 Component Architecture

### ProposalCard Component
**Location:** `src/components/Dashboard/ProposalCard.jsx`

**Features:**
- Interactive card with hover effects
- Status and type badges
- Metrics display
- AI-powered actions
- Vote functionality

### Props

```javascript
<ProposalCard
  id="proposal-123"              // Required: Unique identifier
  title="Project Title"           // Required: Proposal title
  description="Description..."    // Optional: Proposal description
  status="in_review"             // Optional: 'pending' | 'in_review' | 'approved' | 'rejected' | 'expired'
  type="allocation"              // Optional: 'allocation' | 'governance' | 'infrastructure' | 'community'
  date="2025-10-21"              // Optional: Date string
  metrics={{                     // Optional: Metrics object
    poverty_index: 0.75,
    project_impact: 0.85,
    deforestation: 0.45,
    corruption_risk: 0.25
  }}
  onViewDetails={(id) => {...}}  // Optional: Callback when card clicked
  onUpdate={(data) => {...}}     // Optional: Callback when updated
/>
```

## 🔧 Integration with Hooks

### 1. **useGateway Hook**

Provides advanced AI analysis through uAgents gateway.

```javascript
import { useGateway } from '@/hooks/useGateway';

const { 
  requestAllocation,    // Submit allocation request
  requestExplanation,   // Request explanation
  pollStatus,           // Poll request status
  checkHealth,          // Check gateway health
  getMetrics,          // Get gateway metrics
  loading,             // Loading state
  polling,             // Polling state
  error                // Error state
} = useGateway();
```

**ProposalCard Usage:**
- Calls `requestAllocation()` when "AI Analysis" button clicked
- Automatically handles FormData creation
- Shows loading state and toast notifications

### 2. **useMeTTa Hook**

Provides fast local priority calculations using MeTTa engine.

```javascript
import { useMeTTa } from '@/hooks/useMeTTa';

const { 
  calculatePriority,      // Calculate priority score
  generateExplanation,    // Generate explanation
  checkHealth,            // Check MeTTa health
  loading,                // Loading state
  error                   // Error state
} = useMeTTa();
```

**ProposalCard Usage:**
- Calls `calculatePriority()` when "Priority" button clicked
- Uses metrics prop for calculation
- Displays result in toast notification

### 3. **proposalsAPI**

Backend API integration for proposal operations.

```javascript
import { proposalsAPI } from '@/services/api';

// Available methods
proposalsAPI.list(params)           // List proposals
proposalsAPI.get(id)                // Get proposal details
proposalsAPI.create(data)           // Create new proposal
proposalsAPI.update(id, data)       // Update proposal
proposalsAPI.vote(id, voteData)     // Vote on proposal
```

**ProposalCard Usage:**
- Calls `vote()` method for voting functionality
- Handles authentication automatically
- Shows success/error toasts

## 🚀 Usage Examples

### Basic Usage

```javascript
import ProposalCard from '@/components/Dashboard/ProposalCard';

function MyComponent() {
  return (
    <ProposalCard
      id="1"
      title="Community Water Project"
      status="in_review"
      type="infrastructure"
      date="2025-10-21"
      metrics={{
        poverty_index: 0.75,
        project_impact: 0.85
      }}
    />
  );
}
```

### With Callbacks

```javascript
import ProposalCard from '@/components/Dashboard/ProposalCard';
import { useNavigate } from 'react-router-dom';

function ProposalsList() {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState([...]);

  const handleViewDetails = (id) => {
    navigate(`/proposals/${id}`);
  };

  const handleUpdate = (updatedData) => {
    setProposals(prev => 
      prev.map(p => 
        p.id === updatedData.id 
          ? { ...p, ...updatedData } 
          : p
      )
    );
  };

  return (
    <div className="grid grid-cols-3 gap-4">
      {proposals.map(proposal => (
        <ProposalCard
          key={proposal.id}
          {...proposal}
          onViewDetails={handleViewDetails}
          onUpdate={handleUpdate}
        />
      ))}
    </div>
  );
}
```

### Fetching from API

```javascript
import { useState, useEffect } from 'react';
import { proposalsAPI } from '@/services/api';
import ProposalCard from '@/components/Dashboard/ProposalCard';

function ProposalsPage() {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    try {
      const response = await proposalsAPI.list({ status: 'in_review' });
      setProposals(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {proposals.map(proposal => (
        <ProposalCard
          key={proposal.id}
          {...proposal}
          onUpdate={loadProposals}
        />
      ))}
    </div>
  );
}
```

## 🎨 Styling & Theming

### Status Colors

```javascript
const statusColors = {
  'pending': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'in_review': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'approved': 'bg-green-500/20 text-green-400 border-green-500/30',
  'rejected': 'bg-red-500/20 text-red-400 border-red-500/30',
  'expired': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};
```

### Type Colors

```javascript
const typeColors = {
  'allocation': 'bg-violet-500/20 text-violet-400',
  'governance': 'bg-indigo-500/20 text-indigo-400',
  'infrastructure': 'bg-cyan-500/20 text-cyan-400',
  'community': 'bg-pink-500/20 text-pink-400',
};
```

## 🔍 Action Buttons

### Priority Button (MeTTa)
- Uses local MeTTa engine
- Fast calculation (~100ms)
- Works offline
- Shows result in toast

### AI Analysis Button (Gateway)
- Advanced AI analysis
- Supports PDF uploads (in parent)
- Async processing
- Returns request_id for polling

## 📊 Data Flow

```
1. User clicks "Priority" button
   ↓
2. ProposalCard calls useMeTTa.calculatePriority()
   ↓
3. Hook calls mettaAPI.calculatePriority()
   ↓
4. API sends POST to /api/metta/calculate-priority/
   ↓
5. Django backend processes with MeTTa engine
   ↓
6. Result returned to component
   ↓
7. Toast notification shown
   ↓
8. onUpdate callback triggered (if provided)
```

## 🛠️ Customization

### Add Custom Actions

```javascript
const ProposalCard = ({ ... }) => {
  // ... existing code

  const handleCustomAction = async (e) => {
    e.stopPropagation();
    // Your custom logic
  };

  return (
    // ... existing JSX
    <Button onClick={handleCustomAction}>
      Custom Action
    </Button>
  );
};
```

### Modify Metrics Display

```javascript
// In ProposalCard.jsx, find the metrics section:
{metrics && Object.keys(metrics).length > 0 && (
  <div className="grid grid-cols-2 gap-2 p-2 bg-slate-900/50 rounded-md">
    {Object.entries(metrics).map(([key, value]) => (
      // Customize this section
    ))}
  </div>
)}
```

## 🧪 Testing

See the demo component for a complete working example:
- **File:** `src/components/Dashboard/ProposalCardDemo.jsx`
- **Usage:** Import and render in any page to see all features

## 📚 API Reference

### MeTTa API
- **Endpoint:** `/api/metta/calculate-priority/`
- **Method:** POST
- **Auth:** Not required (public)
- **Body:** `{ poverty_index, project_impact, deforestation, corruption_risk }`

### Gateway API
- **Endpoint:** `/api/gateway/allocation/request/`
- **Method:** POST
- **Auth:** Not required (public)
- **Body:** FormData with metrics and optional files

### Proposals API
- **Endpoint:** `/api/proposals/:id/vote/`
- **Method:** POST
- **Auth:** Required
- **Body:** `{ vote_type: 'approve' | 'reject' }`

## ✅ Checklist

Before using ProposalCard in production:

- [ ] Backend APIs are running (Django on port 8000)
- [ ] MeTTa engine is configured
- [ ] Gateway is running (if using AI Analysis)
- [ ] Component props are correctly passed
- [ ] Callbacks (onViewDetails, onUpdate) are implemented
- [ ] Error handling is in place
- [ ] Loading states are handled
- [ ] Toast notifications are configured (Sonner)

## 🔗 Related Files

- `src/hooks/useGateway.js` - Gateway hook
- `src/hooks/useMeTTa.js` - MeTTa hook
- `src/services/api.js` - API service layer
- `src/components/Dashboard/ProposalCardDemo.jsx` - Demo component

---

**Need help?** Check the demo component or review the individual hook documentation.
