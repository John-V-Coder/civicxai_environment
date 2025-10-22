# 🎯 Allocation Requests Integration Guide

## Overview

This guide shows how allocation requests from AI Gateway now appear beautifully in your dashboard using the new **AllocationRequestCard** and **AllocationRequestsSection** components.

---

## 🏗️ What Was Built

### 1. **Backend Model** (`AllocationRequest`)
Stores all allocation requests with:
- Region information
- Metrics (poverty, impact, environment, risk)
- AI analysis results
- Files attached
- Status tracking

### 2. **API Endpoints**
- `GET /api/allocation-requests/` - List all requests
- `POST /api/allocation-requests/create/` - Create new request
- `GET /api/allocation-requests/<id>/` - Get specific request
- `PUT /api/allocation-requests/<id>/` - Update request
- `DELETE /api/allocation-requests/<id>/` - Delete request
- `GET /api/allocation-requests/stats/` - Get statistics

### 3. **Frontend Components**
- `AllocationRequestCard.jsx` - Beautiful card display
- `AllocationRequestsSection.jsx` - Dashboard section with filtering

### 4. **Auto-Save Integration**
AIGateway now automatically saves requests to dashboard when submitted!

---

## 📦 Installation Steps

### Step 1: Run Database Migrations

```bash
cd civicxai_backend

# Create migrations for new AllocationRequest model
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 2: No Frontend Changes Needed!

The integration is already complete in `AIGateway.jsx`. When users submit allocation requests, they're automatically saved to the database.

### Step 3: Add to Your Dashboard

Add the `AllocationRequestsSection` component to your dashboard page:

```javascript
// In your Dashboard.jsx or main dashboard file
import AllocationRequestsSection from '@/components/Dashboard/AllocationRequestsSection';

function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Your existing dashboard content */}
      
      {/* Add this section */}
      <AllocationRequestsSection />
    </div>
  );
}
```

---

## 🎨 Component Features

### AllocationRequestCard

**Beautiful, user-friendly display with:**

✅ **Prominent Region Name** at the top with map icon
✅ **Status Badge** (Pending, Processing, Analyzed, Approved)
✅ **Priority Level** badge (CRITICAL, HIGH, MEDIUM, LOW)
✅ **Confidence Score** percentage
✅ **Visual Metrics** with progress bars:
   - Poverty Index (red)
   - Project Impact (green)
   - Environmental Score (blue)
   - Corruption Risk (orange)
✅ **AI Recommendation** percentage in gradient box
✅ **Key Findings** bullets (first 2 shown)
✅ **Files Attached** indicator
✅ **Timestamp** with analysis status
✅ **Hover Effects** with smooth animations

### AllocationRequestsSection

**Complete dashboard section with:**

✅ **Statistics Cards** (Total, Pending, Processing, Analyzed, Approved)
✅ **Search** by region name or ID
✅ **Filter Tabs** by status
✅ **Refresh** button
✅ **Responsive Grid** layout (1-3 columns)
✅ **Empty States** with helpful messages
✅ **Smooth Animations** on load

---

## 🔄 How It Works

### Flow Diagram

```
User Submits in AIGateway
          ↓
1. Save to Database (allocationRequestsAPI.create)
          ↓
2. Submit to Gateway API for AI analysis
          ↓
3. Poll for results
          ↓
4. Update database with AI results (allocationRequestsAPI.update)
          ↓
5. Display immediately in Dashboard!
```

### Data Flow

```javascript
// Step 1: User fills form in AIGateway
{
  region_id: "REG-001",
  poverty_index: 0.85,
  project_impact: 0.90,
  // ... other metrics
}

// Step 2: Saved to database
POST /api/allocation-requests/create/
→ Creates AllocationRequest with status="processing"

// Step 3: AI Gateway processes
→ Returns priority_level, confidence, recommendations

// Step 4: Update with AI results
PUT /api/allocation-requests/<id>/
→ Updates with AI analysis, status="analyzed"

// Step 5: Dashboard fetches and displays
GET /api/allocation-requests/
→ AllocationRequestsSection shows beautiful cards
```

---

## 💡 Usage Examples

### Example 1: Submit Allocation Request

```javascript
// User in AI Gateway:
// 1. Fills form with region data
// 2. Uploads PDF files (optional)
// 3. Clicks "Submit to AI Gateway"

// Result:
// ✅ Saved to database instantly
// ✅ Appears in dashboard immediately
// ✅ Shows "Processing" status
// ✅ Updates to "Analyzed" when AI completes
```

### Example 2: View in Dashboard

```javascript
// Navigate to Dashboard
// See AllocationRequestsSection with:

// Statistics:
// Total: 15 | Pending: 2 | Processing: 3 | Analyzed: 8 | Approved: 2

// Cards showing:
┌──────────────────────────────────────┐
│ 📍 North Region (REG-001)            │
│ Status: Analyzed  🔵                 │
│ ⭐ HIGH Priority | Confidence: 85%   │
│                                      │
│ Metrics:                             │
│ Poverty ███████░░ 75%                │
│ Impact  ████████░ 90%                │
│ Environment ██████░░░ 70%            │
│ Risk ███░░░░░░░ 30%                  │
│                                      │
│ 🧠 AI Recommendation: 65.5%          │
│                                      │
│ Key Findings:                        │
│ • High poverty requires immediate... │
│ • Project impact score excellent...  │
│                                      │
│ 🕒 Oct 22, 2025 at 4:20am           │
└──────────────────────────────────────┘
```

### Example 3: Filter and Search

```javascript
// Search Box: "North"
// → Shows only regions with "North" in name

// Filter Tabs: Click "Analyzed"
// → Shows only requests with status="analyzed"

// Refresh Button
// → Fetches latest data from database
```

---

## 🎯 ProposalCard Integration (Optional)

If you want allocation requests to appear in **existing ProposalCard** components:

```javascript
// In your proposals list component
import AllocationRequestCard from '@/components/Dashboard/AllocationRequestCard';

// Mix with proposals
const allItems = [
  ...proposals.map(p => ({ type: 'proposal', data: p })),
  ...allocationRequests.map(r => ({ type: 'allocation', data: r }))
];

// Render
{allItems.map(item => (
  item.type === 'allocation' ? (
    <AllocationRequestCard request={item.data} />
  ) : (
    <ProposalCard proposal={item.data} />
  )
))}
```

---

## 🚀 Quick Start

### 1. Run Migrations

```bash
cd civicxai_backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Start Backend

```bash
python manage.py runserver
```

### 3. Add to Dashboard

```javascript
// src/pages/Dashboard.jsx (or your main dashboard file)
import AllocationRequestsSection from '@/components/Dashboard/AllocationRequestsSection';

export default function Dashboard() {
  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Existing dashboard content */}
      
      {/* NEW: Allocation Requests Section */}
      <AllocationRequestsSection />
    </div>
  );
}
```

### 4. Test It!

1. Navigate to **AI Gateway**
2. Fill allocation form:
   - Region ID: `TEST-001`
   - Poverty: `0.85`
   - Impact: `0.90`
   - Environment: `0.75`
   - Risk: `0.30`
3. Click **"Submit to AI Gateway"**
4. See toast: "Allocation request saved to dashboard!"
5. Navigate to **Dashboard**
6. See your beautiful allocation request card! 🎉

---

## 📊 API Usage

### Fetch All Requests

```javascript
import { allocationRequestsAPI } from '@/services/api';

// Get all
const response = await allocationRequestsAPI.list();

// Filter by status
const pending = await allocationRequestsAPI.list({ status: 'pending' });

// Get stats
const stats = await allocationRequestsAPI.stats();
```

### Create Request (Auto-done by AIGateway)

```javascript
const request = await allocationRequestsAPI.create({
  region_id: 'REG-001',
  region_name: 'North Region',
  poverty_index: 0.85,
  project_impact: 0.90,
  environmental_score: 0.75,
  corruption_risk: 0.30,
  notes: 'High priority region',
  status: 'pending'
});
```

### Update with AI Results (Auto-done by AIGateway)

```javascript
await allocationRequestsAPI.update(requestId, {
  status: 'analyzed',
  priority_level: 'HIGH',
  confidence_score: 0.85,
  recommended_allocation_percentage: 65.5,
  key_findings: [
    'High poverty requires immediate attention',
    'Strong project impact expected'
  ],
  recommendations: [
    { type: 'funding', action: 'Allocate 65% of budget' }
  ]
});
```

---

## 🎨 Customization

### Change Card Colors

```javascript
// In AllocationRequestCard.jsx
const priorityColors = {
  'CRITICAL': 'text-red-400 bg-red-500/20',  // Change these
  'HIGH': 'text-orange-400 bg-orange-500/20',
  'MEDIUM': 'text-yellow-400 bg-yellow-500/20',
  'LOW': 'text-blue-400 bg-blue-500/20',
};
```

### Change Card Layout

```javascript
// In AllocationRequestsSection.jsx
// Change grid columns:
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
// To:
<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
```

### Add More Filters

```javascript
// In AllocationRequestsSection.jsx
const [regionFilter, setRegionFilter] = useState('all');

// Add filter UI
<Select value={regionFilter} onValueChange={setRegionFilter}>
  <SelectTrigger>
    <SelectValue placeholder="Filter by region" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="all">All Regions</SelectItem>
    <SelectItem value="north">North</SelectItem>
    <SelectItem value="south">South</SelectItem>
  </SelectContent>
</Select>
```

---

## 📱 Mobile Responsive

The cards are fully responsive:

- **Mobile (< 768px)**: Single column
- **Tablet (768px - 1280px)**: 2 columns
- **Desktop (> 1280px)**: 3 columns

All text scales appropriately and metrics remain visible.

---

## ✨ Key Features Summary

| Feature | Status | Description |
|---------|--------|-------------|
| **Auto-Save** | ✅ | Requests saved automatically when submitted |
| **Beautiful Cards** | ✅ | Gradient backgrounds, animations, icons |
| **Region Name** | ✅ | Prominently displayed at top |
| **Visual Metrics** | ✅ | Progress bars with colors |
| **AI Results** | ✅ | Priority, confidence, recommendations |
| **Search** | ✅ | By region name or ID |
| **Filter** | ✅ | By status (pending, analyzed, etc.) |
| **Statistics** | ✅ | Count cards for each status |
| **Responsive** | ✅ | Works on all screen sizes |
| **Animations** | ✅ | Smooth hover and load effects |

---

## 🎉 Summary

**Your allocation requests now:**

1. ✅ **Auto-save** when submitted in AI Gateway
2. ✅ **Appear instantly** in dashboard
3. ✅ **Look beautiful** with gradients and animations
4. ✅ **Show region name** prominently
5. ✅ **Display all metrics** visually
6. ✅ **Include AI analysis** when complete
7. ✅ **Support filtering** and search
8. ✅ **Update in real-time** as status changes

**Users can now:**
- Submit allocation requests easily
- See all their requests in one place
- Track analysis status
- View AI recommendations
- Search and filter requests
- Get a beautiful, professional UI experience

**Ready to use!** 🚀
