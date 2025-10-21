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
import { useChat } from '@/hooks/useChat';
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
    sendMessage,
    loading,
    error: chatError 
  } = useChat();

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
