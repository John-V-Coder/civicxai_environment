# 📊 MetricCard Integration Guide

## Overview

The enhanced `MetricCard` component is now fully integrated with:
- ✅ **useGateway** hook - Gateway metrics and health checks
- ✅ **useMeTTa** hook - MeTTa engine health monitoring
- ✅ **dashboardAPI** - Backend dashboard metrics
- ✅ **Real-time updates** - Auto-refresh with configurable intervals
- ✅ **Loading states** - Visual feedback during data fetching
- ✅ **Error handling** - Graceful error display

## 📦 Component Architecture

### MetricCard Component
**Location:** `src/components/Dashboard/MetricCard.jsx`

**Key Features:**
- Multiple data sources (static, API, Gateway, MeTTa)
- Auto-refresh with configurable intervals
- Manual refresh button
- Loading and error states
- Status badges (Online/Offline)
- Trend indicators
- Last updated timestamp
- Responsive design

### Props

```javascript
<MetricCard
  // Display Props
  title="Total Users"              // Required: Metric title
  value={2543}                     // Required: Initial/static value
  subtitle="Active members"        // Optional: Subtitle text
  change="+12.5%"                  // Optional: Change indicator
  icon={<Users />}                 // Required: Icon component
  color="blue"                     // Optional: Color theme
  
  // Data Fetching Props
  metricType="gateway"             // Optional: 'static' | 'gateway' | 'gateway_health' | 'metta_health' | 'api'
  endpoint="/api/metrics/"         // Optional: Custom API endpoint
  refreshInterval={30000}          // Optional: Auto-refresh in ms
  
  // UI Props
  showRefresh={true}               // Optional: Show refresh button
  showStatus={false}               // Optional: Show online/offline badge
  className="custom-class"         // Optional: Additional CSS classes
  
  // Callbacks
  onRefresh={(data) => {...}}      // Optional: Called after refresh
/>
```

## 🎨 Color Options

```javascript
const colors = [
  'blue',    // Default blue theme
  'green',   // Green (success, positive)
  'yellow',  // Yellow (warning, attention)
  'purple',  // Purple (info)
  'violet',  // Violet (AI/tech)
  'red'      // Red (error, negative)
];
```

## 🔧 Metric Types

### 1. **Static** (Default)
No API calls, displays provided values only.

```javascript
<MetricCard
  title="Total Users"
  value="2,543"
  subtitle="Community members"
  change="+12.5%"
  icon={<Users className="h-5 w-5" />}
  color="blue"
  // No metricType = static
/>
```

### 2. **Gateway Metrics**
Fetches metrics from uAgents Gateway.

```javascript
<MetricCard
  title="Gateway Requests"
  value="0"
  subtitle="Total processed"
  icon={<Activity className="h-5 w-5" />}
  color="blue"
  metricType="gateway"              // Calls getGatewayMetrics()
  showRefresh={true}
  refreshInterval={15000}           // Refresh every 15 seconds
/>
```

### 3. **Gateway Health**
Monitors Gateway service status.

```javascript
<MetricCard
  title="Gateway Status"
  value="Checking..."
  subtitle="uAgents Gateway"
  icon={<Network className="h-5 w-5" />}
  color="green"
  metricType="gateway_health"       // Calls checkGatewayHealth()
  showStatus={true}                 // Shows Online/Offline badge
  showRefresh={true}
  refreshInterval={30000}           // Refresh every 30 seconds
/>
```

### 4. **MeTTa Health**
Monitors MeTTa engine status.

```javascript
<MetricCard
  title="MeTTa Engine"
  value="Checking..."
  subtitle="Local AI Engine"
  icon={<Brain className="h-5 w-5" />}
  color="violet"
  metricType="metta_health"         // Calls checkMeTTaHealth()
  showStatus={true}
  showRefresh={true}
  refreshInterval={30000}
/>
```

### 5. **API Dashboard**
Fetches from Django dashboard API.

```javascript
<MetricCard
  title="Active Users"
  value="0"
  subtitle="Currently online"
  icon={<Users className="h-5 w-5" />}
  color="green"
  metricType="api"                  // Calls dashboardAPI.getMetrics()
  showRefresh={true}
/>
```

## 🚀 Usage Examples

### Basic Grid Layout

```javascript
import MetricCard from '@/components/Dashboard/MetricCard';
import { Users, DollarSign, Activity, TrendingUp } from 'lucide-react';

function Dashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        title="Total Users"
        value="2,543"
        subtitle="Active members"
        change="+12.5%"
        icon={<Users className="h-5 w-5" />}
        color="blue"
      />
      
      <MetricCard
        title="Total Allocations"
        value="$1.2M"
        subtitle="Distributed funds"
        change="+8.3%"
        icon={<DollarSign className="h-5 w-5" />}
        color="green"
      />
      
      <MetricCard
        title="Active Proposals"
        value="48"
        subtitle="Under review"
        change="-2.1%"
        icon={<Activity className="h-5 w-5" />}
        color="purple"
      />
      
      <MetricCard
        title="Success Rate"
        value="94.2%"
        subtitle="Approved"
        change="+1.8%"
        icon={<TrendingUp className="h-5 w-5" />}
        color="violet"
      />
    </div>
  );
}
```

### Real-time AI Service Monitoring

```javascript
import MetricCard from '@/components/Dashboard/MetricCard';
import { Network, Brain, Zap } from 'lucide-react';

function AIServiceMonitor() {
  const handleRefresh = (data) => {
    console.log('Refreshed:', data);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <MetricCard
        title="Gateway Status"
        value="Online"
        subtitle="uAgents Gateway"
        icon={<Network className="h-5 w-5" />}
        color="green"
        metricType="gateway_health"
        showStatus={true}
        showRefresh={true}
        refreshInterval={30000}
        onRefresh={handleRefresh}
      />
      
      <MetricCard
        title="MeTTa Engine"
        value="Online"
        subtitle="Local AI Engine"
        icon={<Brain className="h-5 w-5" />}
        color="violet"
        metricType="metta_health"
        showStatus={true}
        showRefresh={true}
        refreshInterval={30000}
        onRefresh={handleRefresh}
      />
      
      <MetricCard
        title="Gateway Requests"
        value="156"
        subtitle="Total processed"
        icon={<Zap className="h-5 w-5" />}
        color="blue"
        metricType="gateway"
        showRefresh={true}
        refreshInterval={15000}
        onRefresh={handleRefresh}
      />
    </div>
  );
}
```

### Dynamic Data from API

```javascript
import { useState, useEffect } from 'react';
import MetricCard from '@/components/Dashboard/MetricCard';
import { dashboardAPI } from '@/services/api';

function DynamicMetrics() {
  const [metrics, setMetrics] = useState({
    users: 0,
    proposals: 0,
    allocations: 0
  });

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const response = await dashboardAPI.getMetrics();
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load metrics');
    }
  };

  return (
    <div className="grid grid-cols-3 gap-4">
      <MetricCard
        title="Total Users"
        value={metrics.users}
        icon={<Users className="h-5 w-5" />}
        color="blue"
        metricType="api"
        showRefresh={true}
        onRefresh={(data) => setMetrics(data)}
      />
      {/* More cards... */}
    </div>
  );
}
```

## 📊 Data Flow

```
User Action (or Auto-refresh Timer)
        ↓
handleRefresh() / useEffect()
        ↓
fetchData() - determines metric type
        ↓
    ┌───────┴───────┐
    │               │
    ▼               ▼
Gateway/MeTTa    API Call
Hook Method
    │               │
    └───────┬───────┘
            ↓
    extractMetricValue()
            ↓
    setValue(newValue)
            ↓
    setLastUpdated(now)
            ↓
    onRefresh callback
            ↓
    Toast notification
```

## 🎯 Features

### Loading States
- Shows spinner icon while fetching
- Displays "--" for value during load
- Disabled refresh button while loading

### Error Handling
- Red AlertCircle icon on error
- Error message displayed
- "Error" badge shown if showStatus enabled
- Toast notification on failure

### Status Badges
- Green "Online" badge when healthy
- Red "Error" badge when service down
- Only shown when `showStatus={true}`

### Trend Indicators
- Green ↑ for positive changes (+)
- Red ↓ for negative changes (-)
- Gray - for no change (0)

### Last Updated
- Shows relative time (e.g., "2m ago")
- Updates automatically
- Hidden during loading

### Auto-refresh
- Configurable interval (milliseconds)
- Runs in background
- Cleaned up on unmount

## 🔧 Integration with Hooks

### useGateway Hook

```javascript
const { 
  getMetrics,      // Get gateway metrics
  checkHealth,     // Check gateway health
  loading,         // Loading state
  error           // Error state
} = useGateway();

// Used by metricType: 'gateway' and 'gateway_health'
```

### useMeTTa Hook

```javascript
const { 
  checkHealth,     // Check MeTTa health
  loading,         // Loading state
  error           // Error state
} = useMeTTa();

// Used by metricType: 'metta_health'
```

### dashboardAPI

```javascript
import { dashboardAPI } from '@/services/api';

// Called by metricType: 'api'
const response = await dashboardAPI.getMetrics();
```

## 🎨 Customization

### Custom Color Theme

Add new color to the colorClasses object:

```javascript
const colorClasses = {
  // ... existing colors
  cyan: 'bg-cyan-500/20 border-cyan-500/30',
};

const iconColorClasses = {
  // ... existing colors
  cyan: 'text-cyan-400',
};
```

### Custom Metric Extraction

Modify `extractMetricValue` function to handle your API response:

```javascript
const extractMetricValue = (data, metricTitle) => {
  if (metricTitle === 'Custom Metric') {
    return data.custom_field || 0;
  }
  // ... existing logic
};
```

### Custom Refresh Logic

Override with `onRefresh` callback:

```javascript
<MetricCard
  {...props}
  onRefresh={(data) => {
    // Custom processing
    console.log('Custom refresh logic', data);
    updateMyState(data);
  }}
/>
```

## 🧪 Testing

See the demo component for complete examples:
- **File:** `src/components/Dashboard/MetricCardDemo.jsx`
- **Usage:** Import and render to see all features

## 📚 API Response Format

### Gateway Metrics
```json
{
  "total_requests": 156,
  "successful_requests": 148,
  "success_rate": 0.948,
  "agent_active": true
}
```

### Health Check
```json
{
  "status": "healthy",
  "agent_active": true,
  "timestamp": "2025-10-21T14:30:00Z"
}
```

### Dashboard Metrics
```json
{
  "active_users": 2543,
  "total_proposals": 48,
  "total_allocations": 1200000,
  "success_rate": 0.942
}
```

## ✅ Checklist

Before using MetricCard in production:

- [ ] Backend API is running (Django on port 8000)
- [ ] Gateway is running (if using gateway metrics)
- [ ] MeTTa engine is configured (if using MeTTa health)
- [ ] Props are correctly set
- [ ] Refresh intervals are reasonable (not too frequent)
- [ ] Error handling is tested
- [ ] Loading states work correctly
- [ ] Toast notifications are configured

## 🔗 Related Files

- `src/hooks/useGateway.js` - Gateway integration
- `src/hooks/useMeTTa.js` - MeTTa integration
- `src/services/api.js` - API service layer
- `src/components/Dashboard/MetricCardDemo.jsx` - Demo component
- `src/components/Dashboard/ProposalCard.jsx` - Related component

---

**MetricCard is production-ready with full API integration!** 🚀
