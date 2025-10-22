import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  Send,
  Bot,
  User,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader2,
  Sparkles,
  Calculator,
  Brain
} from 'lucide-react';
import { toast } from 'sonner';
import { allocationRequestsAPI, explanationRequestsAPI } from '@/services/api';
import { useMeTTa } from '@/hooks/useMeTTa';

/**
 * ProposalChat - Interactive AI chat for explaining proposals
 * Uses MeTTa calculations and AI explanations
 */
const ProposalChat = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const [proposal, setProposal] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [priorityData, setPriorityData] = useState(null);
  
  const { calculatePriority } = useMeTTa();

  // Load proposal data and start AI explanation
  useEffect(() => {
    if (id) {
      loadProposal();
    }
  }, [id]);

  // Auto-scroll to latest message
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadProposal = async () => {
    try {
      setLoading(true);
      
      // Try to load from allocation requests API
      const response = await allocationRequestsAPI.get(id);
      
      if (response.data?.success) {
        const proposalData = response.data.data;
        setProposal(proposalData);
        
        // Start AI analysis immediately
        await startAIAnalysis(proposalData);
      }
    } catch (error) {
      console.error('Error loading proposal:', error);
      toast.error('Failed to load proposal data');
    } finally {
      setLoading(false);
    }
  };

  const startAIAnalysis = async (proposalData) => {
    setCalculating(true);
    
    // Add welcome message
    addMessage('bot', `👋 Hello! I'm your AI assistant. Let me analyze the proposal for **${proposalData.region_name || proposalData.region_id}**.`);
    
    try {
      // Step 1: Calculate priority using MeTTa
      addMessage('bot', '🔍 Calculating priority score using MeTTa reasoning engine...');
      
      const metrics = proposalData.metrics || {};
      const calculationData = {
        poverty_index: metrics.poverty_index || proposalData.poverty_index || 0.5,
        project_impact: metrics.project_impact || proposalData.project_impact || 0.5,
        environmental_score: metrics.environmental_score || proposalData.environmental_score || 0.5,
        corruption_risk: metrics.corruption_risk || proposalData.corruption_risk || 0.3
      };
      
      const priorityResult = await calculatePriority(calculationData);
      setPriorityData(priorityResult);
      
      // Step 2: Explain the priority score
      setTimeout(() => {
        explainPriorityScore(priorityResult, calculationData, proposalData);
      }, 500);
      
    } catch (error) {
      console.error('Error in AI analysis:', error);
      addMessage('bot', '⚠️ There was an issue with the analysis. Let me provide a basic explanation based on the available data.');
      provideBasicExplanation(proposalData);
    } finally {
      setCalculating(false);
    }
  };

  const explainPriorityScore = (priorityResult, metrics, proposalData) => {
    const { priority_score, priority_level, recommended_allocation_percentage } = priorityResult;
    
    // Priority Level Explanation
    let urgencyText = '';
    let icon = '';
    
    if (priority_level === 'critical') {
      urgencyText = 'CRITICAL PRIORITY';
      icon = '🔴';
    } else if (priority_level === 'high') {
      urgencyText = 'HIGH PRIORITY';
      icon = '🟠';
    } else if (priority_level === 'medium') {
      urgencyText = 'MEDIUM PRIORITY';
      icon = '🟡';
    } else {
      urgencyText = 'LOW PRIORITY';
      icon = '🟢';
    }
    
    addMessage('bot', `
${icon} **${urgencyText}**

**Priority Score:** ${(priority_score * 100).toFixed(1)}%

This proposal has been classified as **${priority_level} priority** based on MeTTa's AI reasoning engine.
    `);
    
    // Explain why it requires attention
    setTimeout(() => {
      explainWhyAttentionNeeded(metrics, priority_level, proposalData);
    }, 1000);
    
    // Explain allocation rate
    setTimeout(() => {
      explainAllocationRate(recommended_allocation_percentage, priority_score, priority_level);
    }, 2000);
    
    // Provide key findings
    setTimeout(() => {
      provideKeyFindings(priorityResult, metrics);
    }, 3000);
  };

  const explainWhyAttentionNeeded = (metrics, priority_level, proposalData) => {
    const { poverty_index, project_impact, environmental_score, corruption_risk } = metrics;
    
    const reasons = [];
    
    // Analyze poverty
    if (poverty_index >= 0.7) {
      reasons.push(`📉 **High Poverty Rate (${(poverty_index * 100).toFixed(0)}%)**: This region shows significant economic hardship, requiring immediate support to improve living conditions.`);
    } else if (poverty_index >= 0.5) {
      reasons.push(`📊 **Moderate Poverty (${(poverty_index * 100).toFixed(0)}%)**: Economic conditions need attention to prevent further decline.`);
    }
    
    // Analyze project impact
    if (project_impact >= 0.7) {
      reasons.push(`🎯 **Strong Impact Potential (${(project_impact * 100).toFixed(0)}%)**: Investments here will yield substantial returns and positive outcomes for the community.`);
    }
    
    // Analyze environmental factors
    if (environmental_score >= 0.7) {
      reasons.push(`🌍 **Environmental Concerns (${(environmental_score * 100).toFixed(0)}%)**: Significant environmental degradation detected. Conservation efforts are urgent.`);
    }
    
    // Analyze corruption risk
    if (corruption_risk >= 0.6) {
      reasons.push(`⚠️ **Governance Risk (${(corruption_risk * 100).toFixed(0)}%)**: Enhanced oversight and transparency measures will be required.`);
    } else if (corruption_risk <= 0.3) {
      reasons.push(`✅ **Good Governance (${(corruption_risk * 100).toFixed(0)}% risk)**: Strong institutional framework supports effective implementation.`);
    }
    
    const reasonsText = reasons.length > 0 
      ? reasons.join('\n\n')
      : 'This proposal shows balanced conditions across all indicators, requiring standard monitoring and support.';
    
    addMessage('bot', `
### 🔍 Why This Proposal Requires Attention:

${reasonsText}

**Overall Assessment:** This proposal requires **${priority_level}** attention based on the combination of these factors.
    `);
  };

  const explainAllocationRate = (allocation_percentage, priority_score, priority_level) => {
    let explanation = '';
    
    if (allocation_percentage >= 80) {
      explanation = `This is a **major allocation**, reflecting the critical nature of this proposal. Resources should be deployed rapidly with experienced management teams.`;
    } else if (allocation_percentage >= 60) {
      explanation = `This is a **substantial allocation**, indicating high priority. Standard approval processes should be expedited with close monitoring.`;
    } else if (allocation_percentage >= 40) {
      explanation = `This is a **moderate allocation**, appropriate for the identified needs. Regular monitoring and stakeholder engagement are recommended.`;
    } else {
      explanation = `This is a **baseline allocation**, sufficient for current conditions while monitoring for changes that might require adjustment.`;
    }
    
    addMessage('bot', `
### 💰 Recommended Allocation Rate:

**${allocation_percentage.toFixed(1)}%** of available budget

${explanation}

**Rationale:** The MeTTa reasoning engine calculated this allocation based on:
- Priority Score: ${(priority_score * 100).toFixed(1)}%
- Weighted analysis of poverty (40%), impact (30%), environment (20%), and governance (10%)
- Risk-adjusted resource optimization
    `);
  };

  const provideKeyFindings = (priorityResult, metrics) => {
    const { key_findings, recommendations } = priorityResult;
    
    let findingsText = '';
    if (key_findings && key_findings.length > 0) {
      findingsText = key_findings.map((finding, i) => `${i + 1}. ${finding}`).join('\n');
    } else {
      findingsText = 'Analysis complete based on available metrics.';
    }
    
    let recommendationsText = '';
    if (recommendations && recommendations.length > 0) {
      recommendationsText = recommendations.map((rec, i) => `${i + 1}. ${rec}`).join('\n');
    }
    
    addMessage('bot', `
### 📋 Key Findings:

${findingsText}

${recommendationsText ? `### 💡 Recommendations:\n\n${recommendationsText}` : ''}

---

Feel free to ask me any questions about this analysis! For example:
- "Why is the poverty index so high?"
- "What are the implementation risks?"
- "How can we improve the allocation?"
    `);
  };

  const provideBasicExplanation = (proposalData) => {
    const { region_name, region_id, status, created_at } = proposalData;
    
    addMessage('bot', `
### 📊 Proposal Overview:

**Region:** ${region_name || region_id}
**Status:** ${status || 'Pending'}
**Submitted:** ${created_at ? new Date(created_at).toLocaleDateString() : 'N/A'}

This proposal is currently under review. Available data suggests standard evaluation protocols are being followed.

You can ask me questions about:
- Implementation strategy
- Risk mitigation
- Expected outcomes
- Resource allocation
    `);
  };

  const addMessage = (sender, text) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      sender,
      text,
      timestamp: new Date()
    }]);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message
    addMessage('user', userMessage);
    
    // Generate AI response based on context
    setTimeout(() => {
      generateAIResponse(userMessage);
    }, 500);
  };

  const generateAIResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Context-aware responses
    if (lowerMessage.includes('poverty') || lowerMessage.includes('poor')) {
      if (priorityData && proposal) {
        const povertyIndex = proposal.poverty_index || proposal.metrics?.poverty_index || 0.5;
        addMessage('bot', `
The poverty index of ${(povertyIndex * 100).toFixed(0)}% indicates ${povertyIndex >= 0.7 ? 'significant economic hardship' : 'moderate economic conditions'} in this region. 

This metric contributes **40%** to the overall priority score, making it the most weighted factor in our analysis. ${povertyIndex >= 0.7 ? 'Immediate economic support programs are recommended.' : 'Standard development programs should be maintained.'}
        `);
      } else {
        addMessage('bot', 'The poverty index is a key indicator of economic conditions. Higher values indicate greater need for support.');
      }
    } else if (lowerMessage.includes('risk') || lowerMessage.includes('corruption')) {
      if (priorityData && proposal) {
        const corruptionRisk = proposal.corruption_risk || proposal.metrics?.corruption_risk || 0.3;
        addMessage('bot', `
The corruption risk is assessed at ${(corruptionRisk * 100).toFixed(0)}%. 

${corruptionRisk >= 0.6 ? '⚠️ **High Risk**: Enhanced oversight mechanisms, third-party audits, and transparent digital payment systems are strongly recommended.' : '✅ **Acceptable Risk**: Standard monitoring protocols should be sufficient, though regular audits are still advised.'}

This factor contributes **10%** to the priority calculation but significantly impacts implementation strategy.
        `);
      } else {
        addMessage('bot', 'Corruption risk assessment helps determine the level of oversight and transparency measures needed for successful implementation.');
      }
    } else if (lowerMessage.includes('impact') || lowerMessage.includes('benefit')) {
      if (priorityData && proposal) {
        const projectImpact = proposal.project_impact || proposal.metrics?.project_impact || 0.5;
        addMessage('bot', `
The project impact score is ${(projectImpact * 100).toFixed(0)}%, indicating ${projectImpact >= 0.7 ? 'strong potential for positive outcomes' : 'moderate expected benefits'}.

This metric (30% weight) measures the anticipated effectiveness and reach of investments. ${projectImpact >= 0.7 ? 'High-impact projects should be prioritized for maximum community benefit.' : 'Benefits will be realized through sustained engagement and proper implementation.'}
        `);
      } else {
        addMessage('bot', 'Project impact measures the expected benefits and effectiveness of resource allocation in the region.');
      }
    } else if (lowerMessage.includes('environment') || lowerMessage.includes('ecological')) {
      if (priorityData && proposal) {
        const envScore = proposal.environmental_score || proposal.metrics?.environmental_score || 0.5;
        addMessage('bot', `
The environmental score of ${(envScore * 100).toFixed(0)}% ${envScore >= 0.7 ? 'indicates significant ecological challenges' : 'shows manageable environmental conditions'}.

Contributing **20%** to the priority score, this factor considers deforestation, air quality, water scarcity, and other ecological indicators. ${envScore >= 0.7 ? 'Conservation and restoration programs should be integrated into development plans.' : 'Standard environmental safeguards should be maintained.'}
        `);
      } else {
        addMessage('bot', 'Environmental factors assess the ecological health and sustainability considerations for the region.');
      }
    } else if (lowerMessage.includes('allocation') || lowerMessage.includes('budget') || lowerMessage.includes('funding')) {
      if (priorityData) {
        addMessage('bot', `
Based on the comprehensive MeTTa analysis, **${priorityData.recommended_allocation_percentage?.toFixed(1)}%** of the available budget is recommended for this proposal.

This allocation is calculated using:
- **Priority Score**: ${(priorityData.priority_score * 100).toFixed(1)}%
- **Weighted Factors**: Poverty (40%), Impact (30%), Environment (20%), Governance (10%)
- **Risk Adjustment**: Optimized for effective resource utilization

The allocation can be adjusted based on actual budget availability and competing priorities.
        `);
      } else {
        addMessage('bot', 'The allocation percentage is determined by the priority score and weighted analysis of regional factors.');
      }
    } else if (lowerMessage.includes('calculate') || lowerMessage.includes('recalculate')) {
      addMessage('bot', 'Let me recalculate the priority score for you...');
      if (proposal) {
        startAIAnalysis(proposal);
      }
    } else {
      // Generic helpful response
      addMessage('bot', `
I'm here to help explain this proposal's priority assessment. You can ask me about:

🎯 **Specific Metrics**
- Poverty levels and economic conditions
- Project impact and expected benefits
- Environmental factors and sustainability
- Corruption risk and governance

💰 **Resource Allocation**
- Budget recommendations
- Allocation rationale
- Implementation strategy

📊 **Analysis Details**
- How priority is calculated
- Why this proposal needs attention
- Risk factors and mitigation

What would you like to know more about?
      `);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-violet-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="text-slate-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          
          {proposal && (
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-violet-400" />
                {proposal.region_name || proposal.region_id}
              </h1>
              <p className="text-slate-400 text-sm">AI-Powered Proposal Analysis</p>
            </div>
          )}
          
          {priorityData && (
            <Badge 
              variant="outline" 
              className={`text-lg px-4 py-2 ${
                priorityData.priority_level === 'critical' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                priorityData.priority_level === 'high' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                priorityData.priority_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                'bg-green-500/20 text-green-400 border-green-500/30'
              }`}
            >
              {priorityData.priority_level?.toUpperCase()} PRIORITY
            </Badge>
          )}
        </div>

        {/* Priority Summary Card */}
        {priorityData && (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Calculator className="w-5 h-5 text-violet-400" />
                MeTTa Analysis Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-900/50 p-4 rounded-lg">
                  <div className="text-slate-400 text-sm mb-1">Priority Score</div>
                  <div className="text-2xl font-bold text-white">
                    {(priorityData.priority_score * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg">
                  <div className="text-slate-400 text-sm mb-1">Recommended Allocation</div>
                  <div className="text-2xl font-bold text-violet-400">
                    {priorityData.recommended_allocation_percentage?.toFixed(1)}%
                  </div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg">
                  <div className="text-slate-400 text-sm mb-1">Confidence</div>
                  <div className="text-2xl font-bold text-green-400">
                    {(priorityData.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Chat Interface */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="border-b border-slate-700">
            <CardTitle className="text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-violet-400" />
              AI Assistant Chat
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {/* Messages Area */}
            <div className="h-[500px] overflow-y-auto p-6 space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className={`flex gap-3 ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.sender === 'bot' ? 'bg-violet-500/20' : 'bg-blue-500/20'
                    }`}>
                      {message.sender === 'bot' ? (
                        <Bot className="w-5 h-5 text-violet-400" />
                      ) : (
                        <User className="w-5 h-5 text-blue-400" />
                      )}
                    </div>
                    <div className={`flex-1 max-w-[80%] ${message.sender === 'user' ? 'text-right' : ''}`}>
                      <div className={`inline-block p-4 rounded-lg ${
                        message.sender === 'bot' 
                          ? 'bg-slate-900/50 text-slate-200' 
                          : 'bg-violet-600/30 text-white'
                      }`}>
                        <div className="prose prose-invert prose-sm max-w-none">
                          {message.text.split('\n').map((line, i) => (
                            <p key={i} className="mb-2 last:mb-0">{line}</p>
                          ))}
                        </div>
                      </div>
                      <div className="text-xs text-slate-500 mt-1 px-2">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                {calculating && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex gap-3"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center">
                      <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
                    </div>
                    <div className="flex-1">
                      <div className="inline-block p-4 rounded-lg bg-slate-900/50">
                        <div className="text-slate-400">Analyzing...</div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-slate-700 p-4">
              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about this proposal..."
                  className="flex-1 bg-slate-900 border-slate-700 text-white"
                  disabled={calculating}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || calculating}
                  className="bg-violet-600 hover:bg-violet-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProposalChat;
