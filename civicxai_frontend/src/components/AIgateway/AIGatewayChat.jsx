import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
  Activity,
  ArrowLeft,
  Calculator,
  TrendingUp,
  Search,
  Zap,
  Shield,
  BookOpen,
  Paperclip
} from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import { useMeTTa } from '@/hooks/useMeTTa';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { allocationRequestsAPI } from '@/services/api';

/**
 * AI Gateway Chat Interface
 * Interactive chat platform for asking AI questions and getting explanations
 * Supports both general chat and proposal-specific analysis
 */
const AIGatewayChat = () => {
  const navigate = useNavigate();
  const { id: proposalId } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  
  const scrollRef = useRef(null);
  const fileInputRef = useRef(null);

  const { 
    sendMessage,
    loading,
    error: chatError 
  } = useChat();
  
  const { calculatePriority } = useMeTTa();
  
  const [proposal, setProposal] = useState(null);
  const [priorityData, setPriorityData] = useState(null);
  const [calculating, setCalculating] = useState(false);

  // Load proposal if ID provided
  useEffect(() => {
    if (proposalId) {
      loadProposal();
    }
  }, [proposalId]);

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
   * Load proposal data for specific proposal analysis
   */
  const loadProposal = async () => {
    try {
      setCalculating(true);
      const response = await allocationRequestsAPI.get(proposalId);
      
      if (response.data?.success) {
        const proposalData = response.data.data;
        setProposal(proposalData);
        
        // Start AI analysis
        await analyzeProposal(proposalData);
      }
    } catch (error) {
      console.error('Error loading proposal:', error);
      toast.error('Failed to load proposal data');
      addMessage('bot', 'Sorry, I couldn\'t load the proposal data. Please try again.');
    } finally {
      setCalculating(false);
    }
  };

  /**
   * Analyze proposal using MeTTa
   */
  const analyzeProposal = async (proposalData) => {
    addMessage('bot', `Hello! I'm analyzing the proposal for **${proposalData.region_name || proposalData.region_id}**...`);
    
    try {
      const metrics = proposalData.metrics || {};
      const calculationData = {
        poverty_index: metrics.poverty_index || proposalData.poverty_index || 0.5,
        project_impact: metrics.project_impact || proposalData.project_impact || 0.5,
        environmental_score: metrics.environmental_score || proposalData.environmental_score || 0.5,
        corruption_risk: metrics.corruption_risk || proposalData.corruption_risk || 0.3
      };
      
      const priorityResult = await calculatePriority(calculationData);
      setPriorityData(priorityResult);
      
      // Explain results
      setTimeout(() => {
        explainPriorityResults(priorityResult, calculationData, proposalData);
      }, 500);
      
    } catch (error) {
      console.error('Error analyzing proposal:', error);
      addMessage('bot', 'Analysis complete. You can ask me questions about this proposal.');
    }
  };

  /**
   * Explain priority results
   */
  const explainPriorityResults = (priorityResult, metrics, proposalData) => {
    const { priority_score, priority_level, recommended_allocation_percentage } = priorityResult;
    
    addMessage('bot', `
**${priority_level?.toUpperCase() || 'MEDIUM'} PRIORITY**

**Priority Score:** ${(priority_score * 100).toFixed(1)}%
**Recommended Allocation:** ${recommended_allocation_percentage?.toFixed(1)}%

This proposal has been analyzed using MeTTa's AI reasoning engine based on:
- Poverty Index: ${(metrics.poverty_index * 100).toFixed(0)}%
- Project Impact: ${(metrics.project_impact * 100).toFixed(0)}%
- Environmental Score: ${(metrics.environmental_score * 100).toFixed(0)}%
- Corruption Risk: ${(metrics.corruption_risk * 100).toFixed(0)}%

Feel free to ask me questions about specific metrics, allocation rationale, or implementation strategy!
    `);
  };

  /**
   * Add message to chat
   */
  const addMessage = (type, content) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      type,
      content,
      timestamp: new Date()
    }]);
  };


  /**
   * Process user message and get AI response from backend
   */
  const processMessage = async (userMessage) => {
    setIsTyping(true);

    try {
      // Send message to backend with files
      const response = await sendMessage(userMessage, files.length > 0 ? files : null);
      
      // Add bot response to messages
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: response.content,
        timestamp: new Date(),
        isError: response.isError || false,
        data: response.intent ? { intent: response.intent } : undefined
      }]);

      // Clear files after processing
      setFiles([]);

    } catch (error) {
      console.error('Error processing message:', error);
      
      // Error is already handled by useChat hook
      // Just display a generic error message
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
        isError: true
      }]);
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

  /**
   * Get priority level color
   */
  const getPriorityColor = (level) => {
    switch(level) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-green-500/20 text-green-400 border-green-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900">
      <div className="container mx-auto p-6 space-y-4 max-w-7xl">
        {/* Back Button */}
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            onClick={() => navigate(proposalId ? '/dashboard' : '/ai-gateway')}
            className="text-slate-400 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            {proposalId ? 'Back to Dashboard' : 'Back to Gateway Hub'}
          </Button>
          
          {proposal && (
            <div className="text-right">
              <h2 className="text-xl font-bold text-white">{proposal.region_name || proposal.region_id}</h2>
              <p className="text-sm text-slate-400">Proposal Analysis</p>
            </div>
          )}
        </div>
        
        {/* Priority Summary for Proposals */}
        {priorityData && proposal && (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Calculator className="w-5 w-5 text-violet-400" />
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
                  <div className="text-slate-400 text-sm mb-1">Priority Level</div>
                  <Badge className={`text-lg ${getPriorityColor(priorityData.priority_level)}`}>
                    {priorityData.priority_level?.toUpperCase()}
                  </Badge>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg">
                  <div className="text-slate-400 text-sm mb-1">Recommended Allocation</div>
                  <div className="text-2xl font-bold text-violet-400">
                    {priorityData.recommended_allocation_percentage?.toFixed(1)}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="flex flex-col" style={{ height: 'calc(100vh - 16rem)' }}>

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden relative" style={{ minHeight: 0 }}>
          {messages.length === 0 && !proposalId ? (
            /* Empty State - Welcome Screen */
            <div className="h-full flex flex-col items-center justify-center p-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center max-w-2xl space-y-6"
              >
                <div className="flex items-center justify-center gap-3 mb-4">
                  <Brain className="h-10 w-10 text-blue-400" />
                  <h1 className="text-4xl font-bold text-white">AI Gateway</h1>
                </div>
                
                {/* Compact Cards Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
                  <Card className="bg-slate-800/50 border-slate-700 hover:border-blue-500/50 transition-all cursor-pointer group p-3">
                    <CardContent className="p-0 text-center">
                      <div className="p-2 rounded-lg bg-blue-500/20 group-hover:bg-blue-500/30 transition-colors mb-2 mx-auto w-10 h-10 flex items-center justify-center">
                        <Calculator className="h-5 w-5 text-blue-400" />
                      </div>
                      <h3 className="text-white text-xs font-medium mb-1">Priority Calculations</h3>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-slate-800/50 border-slate-700 hover:border-purple-500/50 transition-all cursor-pointer group p-3">
                    <CardContent className="p-0 text-center">
                      <div className="p-2 rounded-lg bg-purple-500/20 group-hover:bg-purple-500/30 transition-colors mb-2 mx-auto w-10 h-10 flex items-center justify-center">
                        <BookOpen className="h-5 w-5 text-purple-400" />
                      </div>
                      <h3 className="text-white text-xs font-medium mb-1">Explanations</h3>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-slate-800/50 border-slate-700 hover:border-green-500/50 transition-all cursor-pointer group p-3">
                    <CardContent className="p-0 text-center">
                      <div className="p-2 rounded-lg bg-green-500/20 group-hover:bg-green-500/30 transition-colors mb-2 mx-auto w-10 h-10 flex items-center justify-center">
                        <TrendingUp className="h-5 w-5 text-green-400" />
                      </div>
                      <h3 className="text-white text-xs font-medium mb-1">Metrics Analysis</h3>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-slate-800/50 border-slate-700 hover:border-orange-500/50 transition-all cursor-pointer group p-3">
                    <CardContent className="p-0 text-center">
                      <div className="p-2 rounded-lg bg-orange-500/20 group-hover:bg-orange-500/30 transition-colors mb-2 mx-auto w-10 h-10 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-orange-400" />
                      </div>
                      <h3 className="text-white text-xs font-medium mb-1">PDF Analysis</h3>
                    </CardContent>
                  </Card>
                </div>

                <div className="mt-6 flex items-center gap-2 justify-center">
                  <Shield className="h-4 w-4 text-slate-500" />
                  <p className="text-xs text-slate-500">
                    AI-powered by uAgents Gateway • MeTTa Reasoning
                  </p>
                </div>
              </motion.div>
            </div>
          ) : (
          <ScrollArea className="h-full p-6" ref={scrollRef}>
            <div className="max-w-4xl mx-auto space-y-6">
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
                  <Avatar className={`h-9 w-9 flex-shrink-0 ${message.type === 'user' ? 'bg-gradient-to-br from-violet-500 to-purple-600' : 'bg-gradient-to-br from-blue-500 to-cyan-600'}`}>
                    <AvatarFallback>
                      {message.type === 'user' ? (
                        <User className="h-5 w-5 text-white" />
                      ) : (
                        <Brain className="h-5 w-5 text-white" />
                      )}
                    </AvatarFallback>
                  </Avatar>

                  {/* Message Content */}
                  <div className="flex-1">
                    <div className="text-xs text-slate-500 mb-1">
                      {message.type === 'user' ? 'You' : 'AI Assistant'}
                    </div>
                    <div
                      className={`p-4 rounded-2xl ${
                        message.type === 'user'
                          ? 'bg-gradient-to-br from-violet-600 to-purple-700 text-white'
                          : message.isError
                          ? 'bg-red-900/30 border border-red-700 text-slate-300'
                          : 'bg-slate-800/80 text-slate-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
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
                    <p className="text-xs text-slate-600 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing indicator */}
            {(isTyping || calculating) && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <Avatar className="h-9 w-9 bg-gradient-to-br from-blue-500 to-cyan-600">
                  <AvatarFallback>
                    <Brain className="h-5 w-5 text-white" />
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="text-xs text-slate-500 mb-1">AI Assistant</div>
                  <div className="bg-slate-800/80 p-4 rounded-2xl">
                    <div className="flex gap-1.5">
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            </div>
          </ScrollArea>
          )}
        </div>

        {/* Input Area - Enhanced for better typing experience */}
        <div className="border-t border-slate-800/50 p-6 max-w-4xl mx-auto w-full">
          {/* File Preview - Compact */}
          {files.length > 0 && (
            <div className="mb-3 p-2 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-medium text-slate-300 flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  Files ({files.length})
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFiles([])}
                  className="text-xs text-slate-400 hover:text-white h-5 px-2"
                >
                  Clear
                </Button>
              </div>
              <div className="flex flex-wrap gap-1">
                {files.map((file, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-1 px-2 py-1 bg-slate-900 rounded text-xs border border-slate-700"
                  >
                    <FileText className="h-3 w-3 text-blue-400" />
                    <span className="text-slate-300 truncate max-w-[120px]">
                      {file.name}
                    </span>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-slate-400 hover:text-red-400 ml-1"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          <div className="relative w-full">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv"
              onChange={handleFileChange}
              className="hidden"
            />
            
            {/* Enhanced Input Area */}
            <div className="bg-slate-800/80 rounded-2xl border border-slate-700/50 focus-within:border-blue-500/50 transition-all p-1">
              <div className="flex items-center gap-1">
                {/* Compact Action Buttons */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-xl h-8 w-8 p-0"
                  title="Attach files"
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-xl h-8 w-8 p-0"
                  title="Analyze with MeTTa"
                >
                  <Brain className="h-4 w-4" />
                </Button>

                {/* Expanded Input Area */}
                <div className="flex-1 min-w-0">
                  <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    placeholder={proposalId ? "Ask about this proposal..." : "Message AI Assistant..."}
                    className="w-full bg-transparent border-0 text-white placeholder:text-slate-500 focus-visible:ring-0 focus-visible:ring-offset-0 text-[15px] resize-none min-h-[40px] max-h-[120px] py-2"
                    disabled={loading || calculating}
                    rows={1}
                  />
                </div>

                <Button
                  onClick={handleSend}
                  disabled={loading || calculating || (!input.trim() && files.length === 0)}
                  className="bg-blue-600 hover:bg-blue-700 rounded-xl h-8 w-8 p-0 flex-shrink-0"
                  size="icon"
                >
                  {(loading || calculating) ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default AIGatewayChat;