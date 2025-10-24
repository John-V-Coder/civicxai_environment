CivicX Gateway Chat Interface
Overview

The CivicX Gateway Chat Interface provides a conversational way to interact with backend services for allocation analysis, priority calculations, and explanations. Users can ask questions naturally and get instant system-generated responses.

Features
Chat-Based Interaction

Natural language processing

Intent detection

Conversational responses

Real-time message updates

Typing indicators

Message history

Core Capabilities

Priority Calculation – Request priority scores

Allocation Analysis – Get detailed analysis

Explanations – Understand decisions

Health Checks – Check system status

PDF Analysis – Upload documents for insights

File Support

PDF documents

Images (PNG, JPG, JPEG)

Text files (TXT, CSV)

Multiple file uploads

File preview and removal

Component Structure
GatewayChat Component

Location: src/components/Gateway/GatewayChat.jsx

Integrated with:

useGateway hook – Core Gateway processing

useMeTTa hook – Fast local computations

gatewayAPI & mettaAPI – Backend communication

Gateway Component (Updated)

Location: src/components/Gateway/Gateway.jsx

Three tabs:

Chat Assistant – Conversational interface

Allocation Request – Form-based allocation

Explanation Request – Form-based explanation

Natural Language Commands
Priority Calculation
"Calculate priority for poverty 0.8"  
"What's the priority score with impact 0.9?"  
"Calculate priority: poverty 0.75, impact 0.85, corruption 0.3"

Allocation Analysis
"Analyze this region with high poverty"  
"Give me allocation recommendation for poverty 0.8, impact 0.9"  
"Analyze allocation with uploaded PDF"

Explanations
"Explain why this region got high priority"  
"Explain the allocation decision"  
"Why was this region prioritized?"

Health Check
"Check system health"  
"What's the gateway status?"  
"Is everything working?"

Usage Examples
Basic Question

User: "Calculate priority for poverty 0.8"

System Response:
Priority Calculation Complete

Priority Score: 0.76
Confidence: 85.0%

Breakdown:
• Poverty Index: 0.8
• Project Impact: 0.6
• Deforestation: 0.4
• Corruption Risk: 0.3

This score indicates high priority for resource allocation.

With File Upload

User: Uploads PDF + asks "Analyze this region"

System Response:
Analysis Complete

Priority Level: High
Confidence: 92.3%
Recommended Allocation: 75%

Key Findings:
• High poverty indicators identified
• Strong project implementation capacity
• Low corruption risk factors

System Check

User: "Check system status"

System Response:
System Health Check

Gateway Status: healthy
Agent Active: Yes

All systems are operational.

Integration Details
Intent Detection
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
};

Metric Extraction
const extractMetrics = (message) => {
  // "poverty 0.8, impact 0.9" → { poverty_index: 0.8, project_impact: 0.9 }
  const povertyMatch = message.match(/poverty.*?(\d+\.?\d*)/i);
  const impactMatch = message.match(/impact.*?(\d+\.?\d*)/i);
};

API Calls
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

UI Components
Message Types
User Message
<div className="bg-violet-600 text-white p-3 rounded-lg">
  {message.content}
</div>

System Message
<div className="bg-slate-800 border border-slate-700 p-3 rounded-lg">
  {message.content}
</div>

Error Message
<div className="bg-red-900/30 border border-red-700 p-3 rounded-lg"></div>

Typing Indicator
<div className="flex gap-1">
  <span className="animate-bounce">•</span>
  <span className="animate-bounce" style={{animationDelay: '150ms'}}>•</span>
  <span className="animate-bounce" style={{animationDelay: '300ms'}}>•</span>
</div>

Responsive Design

Full-height chat interface

Auto-scroll to latest message

Mobile-friendly layout

Touch-optimized controls

Getting Started

Navigate to Gateway
http://localhost:5173/gateway

Click “Chat Assistant” Tab
The chat interface is now the default tab.

Start Chatting
Type your question or upload files to begin.

Example Message:

"Hello! Can you help me calculate priority for a region with poverty 0.8?"

Chat Flow Example
User: "Hi, I need help with allocation analysis"
System: "Hello! I can help you with allocation analysis. 
         Please provide the metrics or upload documents..."

User: *Uploads PDF* "Analyze this region"
System: "Analyzing your document... 
         Analysis Complete!

         Priority Level: High
         Confidence: 89%"

User: "Why did it get high priority?"
System: "This region received high priority because:
         • Poverty index is above threshold
         • Project impact potential is strong
         ..."

Advanced Features

Context Awareness – remembers previous messages

File Context – analyzes uploaded PDFs for insights

Error Recovery – clear messages and recovery options

Customization
Add New Intents
if (lowerMsg.includes('compare')) {
  return 'compare_regions';
}

Customize Response Format
botResponse = `**Custom Format**\n\n` +
  `Your custom content here\n` +
  `${result.data}`;

Add Quick Actions
<div className="flex gap-2 mt-2">
  <Button size="sm" onClick={() => setInput("Calculate priority")}>
    Quick Priority
  </Button>
  <Button size="sm" onClick={() => setInput("Check health")}>
    Health Check
  </Button>
</div>

Data Flow
User Input
    
detectIntent
    
extractMetrics
    
useMeTTa Hook            useGateway Hook
(Local/Fast)             (Advanced/PDF)
               
        Process Response
               
        Format Message
               
        Add to Chat
               
        Display to User

Best Practices

Be Specific – Provide clear questions

Use Keywords – Include “calculate”, “analyze”, “explain”

Provide Context – Upload relevant documents

Check System Health – Verify system readiness

Review History – Use previous messages for context

Testing

Test Priority Calculation

Input: "Calculate priority for poverty 0.8, impact 0.9"  
Expected: Priority score with breakdown  


Test File Upload

Input: Upload PDF + "Analyze this document"  
Expected: Analysis with file context  


Test Explanation

Input: "Explain why region X got priority"  
Expected: Detailed explanation  

Related Documentation

PROPOSALCARD_INTEGRATION.md – ProposalCard integration

METRICCARD_INTEGRATION.md – MetricCard integration

WALLET_INTEGRATION.md – Wallet features

INTEGRATION_SUMMARY.md – Complete system overview

The Gateway Chat Interface is production-ready! 
Start chatting with the assistant for instant allocation analysis, explanations, and real-time insights.