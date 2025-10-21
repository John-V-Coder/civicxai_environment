import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Brain,
  User,
  Bot,
  Loader2,
  Sparkles,
  Upload,
  FileText,
  Trash2,
  Network,
  Activity
} from 'lucide-react';
import { useGateway } from '@/hooks/useGateway';
import { useMeTTa } from '@/hooks/useMeTTa';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * AI Gateway Chat Interface
 * Interactive chat platform for asking AI questions and getting explanations
 */
const AIGatewayChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your AI assistant powered by uAgents Gateway and MeTTa engine. I can help you with:\n\n• Allocation priority calculations\n• Explaining allocation decisions\n• Analyzing metrics and data\n• PDF document analysis\n\nHow can I assist you today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);

  const { 
    requestAllocation, 
    requestExplanation, 
    pollStatus,
    checkHealth,
    loading: gatewayLoading 
  } = useGateway();
  
  const { 
    calculatePriority, 
    generateExplanation,
    loading: mettaLoading 
  } = useMeTTa();

  const loading = gatewayLoading || mettaLoading;

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      // Find the viewport div inside ScrollArea
      const viewport = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        setTimeout(() => {
          viewport.scrollTop = viewport.scrollHeight;
        }, 100);
      }
    }
  }, [messages, isTyping]);

  /**
   * Detect intent from user message
   */
  const detectIntent = (message) => {
    const lowerMsg = message.toLowerCase();
    
    if (lowerMsg.includes('calculate') || lowerMsg.includes('priority') || lowerMsg.includes('score')) {
      return 'calculate_priority';
    }
    if (lowerMsg.includes('explain') || lowerMsg.includes('explanation') || lowerMsg.includes('why')) {
      return 'explain';
    }
    if (lowerMsg.includes('analyze') || lowerMsg.includes('analysis') || lowerMsg.includes('recommendation')) {
      return 'analyze';
    }
    if (lowerMsg.includes('health') || lowerMsg.includes('status') || lowerMsg.includes('check')) {
      return 'health_check';
    }
    
    return 'general';
  };

  /**
   * Extract metrics from natural language
   */
  const extractMetrics = (message) => {
    const metrics = {
      poverty_index: 0.5,
      project_impact: 0.6,
      deforestation: 0.4,
      corruption_risk: 0.3
    };

    // Simple extraction (can be enhanced with NLP)
    const povertyMatch = message.match(/poverty.*?(\d+\.?\d*)/i);
    const impactMatch = message.match(/impact.*?(\d+\.?\d*)/i);
    const deforestMatch = message.match(/deforest.*?(\d+\.?\d*)/i);
    const corruptionMatch = message.match(/corruption.*?(\d+\.?\d*)/i);

    if (povertyMatch) metrics.poverty_index = parseFloat(povertyMatch[1]);
    if (impactMatch) metrics.project_impact = parseFloat(impactMatch[1]);
    if (deforestMatch) metrics.deforestation = parseFloat(deforestMatch[1]);
    if (corruptionMatch) metrics.corruption_risk = parseFloat(corruptionMatch[1]);

    return metrics;
  };

  /**
   * Process user message and generate AI response
   */
  const processMessage = async (userMessage) => {
    const intent = detectIntent(userMessage);
    setIsTyping(true);

    try {
      let botResponse = '';

      switch (intent) {
        case 'calculate_priority':
          const metrics = extractMetrics(userMessage);
          const priorityResult = await calculatePriority(metrics);
          botResponse = `**Priority Calculation Complete**\n\n` +
            `**Priority Score:** ${priorityResult.priority_score?.toFixed(2) || 'N/A'}\n` +
            `**Confidence:** ${(priorityResult.confidence * 100).toFixed(1)}%\n\n` +
            `**Breakdown:**\n` +
            `• Poverty Index: ${metrics.poverty_index}\n` +
            `• Project Impact: ${metrics.project_impact}\n` +
            `• Deforestation: ${metrics.deforestation}\n` +
            `• Corruption Risk: ${metrics.corruption_risk}\n\n` +
            `${priorityResult.explanation || 'This score indicates the priority level for resource allocation.'}`;
          break;

        case 'analyze':
          const analysisMetrics = extractMetrics(userMessage);
          
          try {
            // Try Gateway first
            const data = {
              region_id: `CHAT_${Date.now()}`,
              ...analysisMetrics
            };
            
            const analysisResponse = await requestAllocation(data, files);
            toast.success('Analysis submitted to AI Gateway');
            
            const finalResult = await pollStatus(analysisResponse.request_id, {
              maxAttempts: 20,
              interval: 2000
            });

            botResponse = `AI Analysis Complete\n\n` +
              `Priority Level: ${finalResult.recommendation?.priority_level || 'Medium'}\n` +
              `Confidence: ${((finalResult.recommendation?.confidence_score || 0.7) * 100).toFixed(1)}%\n` +
              `Recommended Allocation: ${finalResult.recommendation?.recommended_allocation_percentage || 0}%\n\n`;
            
            if (finalResult.recommendation?.key_findings) {
              botResponse += `Key Findings:\n`;
              finalResult.recommendation.key_findings.forEach(finding => {
                botResponse += `• ${finding}\n`;
              });
            }
          } catch (gatewayError) {
            // Fallback to MeTTa on Gateway failure
            console.warn('Gateway failed, falling back to MeTTa:', gatewayError);
            const mettaResult = await calculatePriority(analysisMetrics);
            
            botResponse = `Analysis Complete (Using MeTTa Engine)\n\n` +
              `Priority Score: ${mettaResult.priority_score?.toFixed(2) || 'N/A'}\n` +
              `Confidence: ${(mettaResult.confidence * 100).toFixed(1)}%\n\n` +
              `Note: Gateway unavailable, used local MeTTa engine for basic calculation.\n\n` +
              `Metrics analyzed:\n` +
              `• Poverty Index: ${analysisMetrics.poverty_index}\n` +
              `• Project Impact: ${analysisMetrics.project_impact}\n` +
              `• Deforestation: ${analysisMetrics.deforestation}\n` +
              `• Corruption Risk: ${analysisMetrics.corruption_risk}`;
          }
          break;

        case 'explain':
          const explanationData = {
            region_id: `CHAT_${Date.now()}`,
            allocation_data: extractMetrics(userMessage),
            context: userMessage,
            language: 'en'
          };
          
          const explainResult = await generateExplanation(explanationData);
          botResponse = `**Explanation Generated**\n\n${explainResult.explanation || explainResult.summary || 'Here is the explanation for the allocation decision based on the provided data.'}`;
          break;

        case 'health_check':
          const health = await checkHealth();
          botResponse = `**System Health Check**\n\n` +
            `Gateway Status: ${health.gateway_status || health.status || 'Unknown'}\n` +
            `Agent Active: ${health.agent_active ? 'Yes' : ' No'}\n\n` +
            `All systems are ${health.gateway_status === 'healthy' || health.status === 'healthy' ? 'operational' : 'experiencing issues'}.`;
          break;

        default:
          botResponse = `I understand you're asking about: "${userMessage}"\n\n` +
            `To help you better, please be more specific. You can ask me to:\n\n` +
            `• **Calculate priority** - e.g., "Calculate priority for poverty 0.8, impact 0.9"\n` +
            `• **Analyze allocation** - e.g., "Analyze this region with high poverty"\n` +
            `• **Explain decision** - e.g., "Explain why this region got high priority"\n` +
            `• **Check health** - e.g., "Check system status"\n\n` +
            `You can also upload PDFs for more detailed analysis!`;
      }

      // Add bot response to messages
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: botResponse,
        timestamp: new Date(),
        data: intent !== 'general' ? { intent } : undefined
      }]);

      // Clear files after processing
      setFiles([]);

    } catch (error) {
      console.error('Error processing message:', error);
      
      let errorMessage = '';
      
      if (error.response?.status === 503) {
        errorMessage = 'AI Gateway Offline\n\nThe AI Gateway is not currently running. Please start the gateway server or I can use the local MeTTa engine for basic calculations.';
      } else if (error.response?.status === 500) {
        const backendError = error.response?.data?.error || error.response?.data?.detail || 'Internal server error';
        errorMessage = `Backend Error (500)\n\n${backendError}\n\nPlease check that:\n• Django backend is running on port 8000\n• Gateway service is properly configured\n• All required dependencies are installed`;
      } else if (error.response?.status === 404) {
        errorMessage = 'Endpoint Not Found\n\nThe requested API endpoint does not exist. Please check your backend configuration.';
      } else {
        errorMessage = `Error: ${error.message || 'Failed to process your request. Please try again.'}\n\nStatus: ${error.response?.status || 'Unknown'}`;
      }
      
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: errorMessage,
        timestamp: new Date(),
        isError: true
      }]);
      
      toast.error('Failed to process request');
    } finally {
      setIsTyping(false);
    }
  };

  /**
   * Handle sending a message
   */
  const handleSend = async () => {
    if (!input.trim() && files.length === 0) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      files: files.length > 0 ? files.map(f => f.name) : undefined,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageContent = input;
    setInput('');

    // Process the message
    await processMessage(messageContent);
  };

  /**
   * Handle file upload
   */
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
    toast.success(`${selectedFiles.length} file(s) added`);
  };

  /**
   * Remove a file
   */
  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  /**
   * Clear chat
   */
  const clearChat = () => {
    setMessages([{
      id: 1,
      type: 'bot',
      content: 'Chat cleared. How can I assist you?',
      timestamp: new Date()
    }]);
    setFiles([]);
  };

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 8rem)' }}>
      <Card className="flex-1 bg-slate-900 border-slate-800 flex flex-col" style={{ minHeight: 0 }}>
        {/* Chat Header */}
        <CardHeader className="border-b border-slate-800 pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
                <Brain className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-white">AI Assistant</CardTitle>
                <p className="text-sm text-slate-400 flex items-center gap-2">
                  <Activity className="h-3 w-3" />
                  {loading ? 'Processing...' : 'Online'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-green-500/20 text-green-400 border-green-500/30">
                <Network className="h-3 w-3 mr-1" />
                Gateway
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearChat}
                className="text-slate-400 hover:text-white"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden" style={{ minHeight: 0 }}>
          <ScrollArea className="h-full p-4" ref={scrollRef}>
            <div className="space-y-4">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  {/* Avatar */}
                  <Avatar className={`h-8 w-8 ${message.type === 'user' ? 'bg-violet-500' : 'bg-blue-500'}`}>
                    <AvatarFallback>
                      {message.type === 'user' ? (
                        <User className="h-4 w-4 text-white" />
                      ) : (
                        <Bot className="h-4 w-4 text-white" />
                      )}
                    </AvatarFallback>
                  </Avatar>

                  {/* Message Content */}
                  <div className={`flex-1 max-w-[85%] ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    <div
                      className={`inline-block p-4 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-violet-600 text-white'
                          : message.isError
                          ? 'bg-red-900/30 border border-red-700 text-slate-300'
                          : 'bg-slate-800 border border-slate-700 text-slate-300'
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                      </div>
                      
                      {/* File attachments */}
                      {message.files && message.files.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {message.files.map((file, i) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              <FileText className="h-3 w-3 mr-1" />
                              {file}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <p className="text-xs text-slate-500 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <Avatar className="h-8 w-8 bg-blue-500">
                  <AvatarFallback>
                    <Bot className="h-4 w-4 text-white" />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-slate-800 border border-slate-700 p-3 rounded-lg">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
            </div>
          </ScrollArea>
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-800">
          <CardContent className="p-4">
          {/* File Preview - Enhanced */}
          {files.length > 0 && (
            <div className="mb-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-slate-300 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Attached Files ({files.length})
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFiles([])}
                  className="text-xs text-slate-400 hover:text-white h-6"
                >
                  Clear All
                </Button>
              </div>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="flex items-center justify-between p-2 bg-slate-900 rounded-md border border-slate-700 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <div className="p-2 rounded bg-blue-500/20">
                        <FileText className="h-4 w-4 text-blue-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-200 truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-slate-500">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(index)}
                      className="h-8 w-8 text-slate-400 hover:text-red-400 hover:bg-red-500/10 flex-shrink-0"
                      title="Remove file"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv"
              onChange={handleFileChange}
              className="hidden"
            />
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              className="bg-slate-800 border-slate-700 hover:bg-slate-700 hover:border-blue-500 transition-colors"
              title="Upload files"
            >
              <Upload className="h-4 w-4" />
            </Button>

            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Ask me anything about allocations, priorities, or explanations..."
              className="flex-1 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              disabled={loading}
            />

            <Button
              onClick={handleSend}
              disabled={loading || (!input.trim() && files.length === 0)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          <p className="text-xs text-slate-500 mt-2">
            Try: &quot;Calculate priority for poverty 0.8&quot;, &quot;Explain this allocation&quot;, or &quot;Analyze with uploaded PDFs&quot;
          </p>
          </CardContent>
        </div>
      </Card>
    </div>
  );
};

export default AIGatewayChat;
