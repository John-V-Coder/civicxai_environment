# AI Gateway Chat Interface

## Overview

The AI Gateway Chat Interface provides a conversational way to interact with AI services for allocation analysis, priority calculations, and explanations. Users can ask questions naturally and get instant AI-powered responses.

## Features

### Chat-Based Interaction
- Natural language processing
- Intent detection
- Conversational AI responses
- Real-time message updates
- Typing indicators
- Message history

### AI Capabilities
- **Priority Calculation** - Ask for priority scores
- **Allocation Analysis** - Request detailed analysis
- **Explanations** - Get explanations for decisions
-  **Health Checks** - Check system status
-  **PDF Analysis** - Upload documents for context

### File Support
- PDF documents
- Images (PNG, JPG, JPEG)
- Text files (TXT, CSV)
- Multiple file uploads
- File preview and removal

## Component Structure

### AIGatewayChat Component
**Location:** `src/components/AIgateway/AIGatewayChat.jsx`

**Integrated with:**
- `useGateway` hook - Advanced Gateway AI
- `useMeTTa` hook - Fast local calculations
- `gatewayAPI` & `mettaAPI` - Backend services

### AIGateway Component (Updated)
**Location:** `src/components/AIgateway/AIGateway.jsx`

**Three tabs:**
1. **Chat Assistant** (New) - Conversational interface
2. **Allocation Request** - Form-based allocation
3. **Explanation Request** - Form-based explanation

## Natural Language Commands

### Priority Calculation

"Calculate priority for poverty 0.8"
"What's the priority score with impact 0.9?"
"Calculate priority: poverty 0.75, impact 0.85, corruption 0.3"


### Allocation Analysis

"Analyze this region with high poverty"
"Give me allocation recommendation for poverty 0.8, impact 0.9"
"Analyze allocation with uploaded PDF"


### Explanations

"Explain why this region got high priority"
"Explain the allocation decision"
"Why was this region prioritized?"


### Health Check

"Check system health"
"What's the gateway status?"
"Is everything working?"


## Usage Examples

### Basic Question

**User:** "Calculate priority for poverty 0.8"

**AI Response:**
Priority Calculation Complete

Priority Score: 0.76
Confidence: 85.0%

Breakdown:
• Poverty Index: 0.8
• Project Impact: 0.6
• Deforestation: 0.4
• Corruption Risk: 0.3

This score indicates high priority for resource allocation.
```

### With File Upload

**User:** *Uploads PDF + asks* "Analyze this region"

**AI Response:**
AI Analysis Complete

 Priority Level: High
 Confidence: 92.3%
 Recommended Allocation: 75%

Key Findings:
• High poverty indicators identified
• Strong project implementation capacity
• Low corruption risk factors
```

### System Check

**User:** "Check system status"

**AI Response:**
 System Health Check

Gateway Status: healthy
Agent Active: Yes

All systems are operational.
```

## Integration Details

### Intent Detection
The chat interface automatically detects user intent:

```javascript
const detectIntent = (message) => {
  const lowerMsg = message.toLowerCase();
  
  if (lowerMsg.includes('calculate') || lowerMsg.includes('priority')) {
    return 'calculate_priority';
  }
  if (lowerMsg.includes('explain') || lowerMsg.includes('why')) {
    return 'explain';
  }
  if (lowerMsg.includes('analyze') || lowerMsg.includes('analysis')) {
    return 'analyze';
  }
  // ... more intents
};
```

### Metric Extraction
Extracts numbers from natural language:

```javascript
const extractMetrics = (message) => {
  // "poverty 0.8, impact 0.9" → { poverty_index: 0.8, project_impact: 0.9 }
  const povertyMatch = message.match(/poverty.*?(\d+\.?\d*)/i);
  const impactMatch = message.match(/impact.*?(\d+\.?\d*)/i);
  // ...
};
```

### API Calls
Routes to appropriate service based on intent:

```javascript
switch (intent) {
  case 'calculate_priority':
    const result = await calculatePriority(metrics);
    break;
    
  case 'analyze':
    const response = await requestAllocation(data, files);
    const finalResult = await pollStatus(response.request_id);
    break;
    
  case 'explain':
    const explanation = await generateExplanation(data);
    break;
}
```

## UI Components

### Message Types

#### User Message
<div className="bg-violet-600 text-white p-3 rounded-lg">
  {message.content}
</div>

#### Bot Message
<div className="bg-slate-800 border border-slate-700 p-3 rounded-lg">
  {message.content}
</div>

#### Error Message
<div className="bg-red-900/30 border border-red-700 p-3 rounded-lg">
</div>

### Typing Indicator
<div className="flex gap-1">
  <span className="animate-bounce">•</span>
  <span className="animate-bounce" style={{animationDelay: '150ms'}}>•</span>
  <span className="animate-bounce" style={{animationDelay: '300ms'}}>•</span>
</div>

## Responsive Design

- Full-height chat interface
- Auto-scroll to latest message
- Mobile-friendly layout
- Touch-optimized controls

## Getting Started

### 1. Navigate to AI Gateway
http://localhost:5173/gateway

### 2. Click "Chat Assistant" Tab
The chat interface is now the default tab.

### 3. Start Chatting
Type your question or upload files and ask.

### Example First Message
```
"Hello! Can you help me calculate priority for a region with poverty 0.8?"
```

## Chat Flow Example

```
User: "Hi, I need help with allocation analysis"
Bot:  "Hello! I can help you with allocation analysis. 
       Please provide the metrics or upload documents..."

User: *Uploads PDF* "Analyze this region"
Bot:  "Analyzing your document... 
       Analysis Complete!
       
       Priority Level: High
       Confidence: 89%
       ..."

User: "Why did it get high priority?"
Bot:  "This region received high priority because:
       • Poverty index is above threshold...
       • Project impact potential is strong...
       ..."
```

## Advanced Features

### Context Awareness
- Remembers conversation history
- References previous messages
- Maintains context across multiple questions

### File Context
- Analyzes uploaded PDFs
- Extracts relevant information
- Includes file data in AI requests

### Error Recovery
- Graceful error handling
- Helpful error messages
- Suggestions for recovery

## Customization

### Add New Intents

```javascript
// In detectIntent function
if (lowerMsg.includes('compare')) {
  return 'compare_regions';
}

// In processMessage function
case 'compare_regions':
  // Your comparison logic
  break;
```

### Customize Response Format

```javascript
// Modify bot response generation
botResponse = `🎯 **Custom Format**\n\n` +
  `Your custom content here\n` +
  `${result.data}`;
```

### Add Quick Actions

```jsx
<div className="flex gap-2 mt-2">
  <Button size="sm" onClick={() => setInput("Calculate priority")}>
    Quick Priority
  </Button>
  <Button size="sm" onClick={() => setInput("Check health")}>
    Health Check
  </Button>
</div>
```

## Data Flow

```
User Input
    ↓
detectIntent()
    ↓
extractMetrics()
    ↓
┌──────────────┴──────────────┐
│                             │
↓                             ↓
useMeTTa Hook            useGateway Hook
(Local/Fast)             (Advanced/PDF)
    │                         │
    └──────────┬──────────────┘
               ↓
        Process Response
               ↓
        Format Message
               ↓
        Add to Chat
               ↓
        Display to User
```

## Best Practices

1. **Clear Questions** - Be specific in your requests
2. **Use Keywords** - Include "calculate", "analyze", "explain"
3. **Provide Context** - Upload relevant documents
4. **Check Status** - Use health checks to verify system status
5. **Review History** - Scroll through previous messages for context

## Testing

### Test Priority Calculation
```
Input: "Calculate priority for poverty 0.8, impact 0.9"
Expected: Priority score with breakdown
```

### Test File Upload
```
Input: Upload PDF + "Analyze this document"
Expected: Analysis with file context
```

### Test Explanation
```
Input: "Explain why region X got priority"
Expected: Detailed explanation
```

## Related Documentation

- `PROPOSALCARD_INTEGRATION.md` - ProposalCard integration
- `METRICCARD_INTEGRATION.md` - MetricCard integration
- `WALLET_INTEGRATION.md` - Wallet features
- `INTEGRATION_SUMMARY.md` - Complete system overview

---

**The AI Chat Interface is production-ready!** 🎉

Start chatting with the AI assistant for instant allocation analysis and explanations.
