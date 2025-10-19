
'use client';

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Bot, 
  Send, 
  User, 
  TrendingUp, 
  Shield, 
  Brain,
  Loader2,
  RefreshCw,
  Zap,
  Target,
  Eye,
  Sparkles
} from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { AdvisorPersona } from "@/lib/advisor-persona";
import { ShadowAI } from "@/lib/shadow-ai";
import { HybridSiphonEngine } from "@/lib/siphon-engine";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  mode?: 'SAGE' | 'TACTICAL';
  timestamp: Date;
}

interface SystemStatus {
  aiOnline: boolean;
  marketData: boolean;
  riskEngine: boolean;
  siphonEngine: boolean;
  shadowAI: boolean;
}

export default function AdvisorClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [advisorMode, setAdvisorMode] = useState<'AUTO' | 'SAGE' | 'TACTICAL'>('AUTO');
  const [advisor] = useState(() => new AdvisorPersona());
  const [shadowAI] = useState(() => new ShadowAI());
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    aiOnline: true,
    marketData: true,
    riskEngine: true,
    siphonEngine: true,
    shadowAI: true
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with philosopher greeting
  useEffect(() => {
    const initializeAdvisor = () => {
      const greeting = advisor.generatePhilosopherGreeting();
      setMessages([{
        id: greeting.id,
        role: 'assistant',
        content: greeting.content,
        mode: greeting.mode,
        timestamp: greeting.timestamp
      }]);
    };

    if (messages.length === 0) {
      initializeAdvisor();
    }
  }, [advisor, messages.length]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      // Generate response using the new advisor persona system
      const response = advisor.generateResponse(currentInput, {
        mode: advisorMode === 'AUTO' ? undefined : advisorMode,
        portfolioValue: 125000, // This would come from actual portfolio data
        marketIntelligence: await shadowAI.getMarketIntelligence()
      });

      // Simulate realistic response delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

      const assistantMessage: Message = {
        id: response.id,
        role: 'assistant',
        content: response.content,
        mode: response.mode,
        timestamp: response.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error generating advisor response:', error);
      toast.error('Advisor temporarily unavailable');
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: 'The advisor systems are momentarily offline. Your empire remains secure while I restore full functionality.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleClearChat = () => {
    const greeting = advisor.generatePhilosopherGreeting();
    setMessages([{
      id: greeting.id,
      role: 'assistant',
      content: greeting.content,
      mode: greeting.mode,
      timestamp: greeting.timestamp
    }]);
  };

  const triggerSampleAlert = async () => {
    const marketIntelligence = await shadowAI.getMarketIntelligence();
    const alert = advisor.generateAlert('VOLATILITY_SPIKE', {
      level: 'HIGH',
      implications: 'Increased siphon ratio recommended'
    });

    setMessages(prev => [...prev, {
      id: alert.id,
      role: 'assistant',
      content: alert.content,
      mode: alert.mode,
      timestamp: alert.timestamp
    }]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            🧠 Sovereign AI Advisor
          </h1>
          <p className="text-muted-foreground">
            Dual-mode intelligence: Sage wisdom + Tactical execution
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            onClick={triggerSampleAlert}
            variant="outline" 
            size="sm"
            className="gap-2"
          >
            <Zap className="h-4 w-4" />
            Test Alert
          </Button>
          <Button 
            onClick={handleClearChat}
            variant="outline" 
            size="sm"
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            New Session
          </Button>
        </div>
      </div>

      {/* Enhanced System Status */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Sovereign Systems Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2">
              <Badge variant={systemStatus.aiOnline ? "default" : "destructive"}>
                <Bot className="h-3 w-3 mr-1" />
                AI Advisor: {systemStatus.aiOnline ? 'Online' : 'Offline'}
              </Badge>
              <Badge variant={systemStatus.shadowAI ? "default" : "destructive"}>
                <Eye className="h-3 w-3 mr-1" />
                Shadow.AI: {systemStatus.shadowAI ? 'Active' : 'Offline'}
              </Badge>
              <Badge variant={systemStatus.siphonEngine ? "default" : "destructive"}>
                <Target className="h-3 w-3 mr-1" />
                Siphon: {systemStatus.siphonEngine ? 'Armed' : 'Standby'}
              </Badge>
              <Badge variant={systemStatus.riskEngine ? "default" : "destructive"}>
                <Shield className="h-3 w-3 mr-1" />
                Risk Guard: {systemStatus.riskEngine ? 'Active' : 'Standby'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Advisor Mode
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={advisorMode} onValueChange={(value: 'AUTO' | 'SAGE' | 'TACTICAL') => setAdvisorMode(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="AUTO">Auto (Adaptive)</SelectItem>
                <SelectItem value="SAGE">Sage Mode (Philosophical)</SelectItem>
                <SelectItem value="TACTICAL">Tactical Mode (Direct)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground mt-2">
              {advisorMode === 'AUTO' && 'AI chooses optimal response style'}
              {advisorMode === 'SAGE' && 'Reflective wisdom and strategic perspective'}
              {advisorMode === 'TACTICAL' && 'Direct analysis and actionable intelligence'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Chat Interface */}
      <div className="grid gap-6 h-[600px]">
        <Card className="flex flex-col h-full">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary" />
                Sovereign Advisory Session
              </div>
              <Badge variant="outline" className="text-xs">
                Mode: {advisorMode}
              </Badge>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="flex-1 flex flex-col p-0">
            {/* Messages */}
            <ScrollArea className="flex-1 px-6">
              <div className="space-y-4 pb-4">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className={`flex items-start gap-3 ${
                        message.role === 'user' ? 'flex-row-reverse' : ''
                      }`}
                    >
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user' 
                          ? 'bg-primary text-primary-foreground' 
                          : message.mode === 'SAGE'
                          ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                          : message.mode === 'TACTICAL'
                          ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                          : 'bg-muted'
                      }`}>
                        {message.role === 'user' ? (
                          <User className="h-4 w-4" />
                        ) : message.mode === 'SAGE' ? (
                          <Sparkles className="h-4 w-4" />
                        ) : message.mode === 'TACTICAL' ? (
                          <Target className="h-4 w-4" />
                        ) : (
                          <Bot className="h-4 w-4" />
                        )}
                      </div>
                      
                      <div className={`flex-1 max-w-[85%] ${
                        message.role === 'user' ? 'text-right' : ''
                      }`}>
                        {message.role === 'assistant' && message.mode && (
                          <Badge 
                            variant="outline" 
                            className={`mb-2 text-xs ${
                              message.mode === 'SAGE' 
                                ? 'border-purple-500/50 text-purple-300' 
                                : 'border-orange-500/50 text-orange-300'
                            }`}
                          >
                            {message.mode === 'SAGE' ? '🧘 Sage Mode' : '⚔️ Tactical Mode'}
                          </Badge>
                        )}
                        <div className={`rounded-lg px-4 py-3 ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground ml-auto'
                            : message.mode === 'SAGE'
                            ? 'bg-purple-500/10 border border-purple-500/20'
                            : message.mode === 'TACTICAL'
                            ? 'bg-orange-500/10 border border-orange-500/20'
                            : 'bg-muted'
                        }`}>
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {message.content}
                          </p>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-start gap-3"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-muted rounded-lg px-4 py-2">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Sovereign advisor analyzing...</span>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Enhanced Input with Quick Actions */}
            <div className="border-t bg-card px-6 py-4 space-y-3">
              {/* Quick Action Buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs h-7"
                  onClick={() => setInput("What's my current portfolio status?")}
                  disabled={isLoading}
                >
                  📊 Portfolio Status
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs h-7"
                  onClick={() => setInput("Analyze current market conditions")}
                  disabled={isLoading}
                >
                  📈 Market Analysis
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs h-7"
                  onClick={() => setInput("Should I execute a siphon now?")}
                  disabled={isLoading}
                >
                  💎 Siphon Check
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs h-7"
                  onClick={() => setInput("Give me strategic wisdom for today")}
                  disabled={isLoading}
                >
                  🧘 Sage Wisdom
                </Button>
              </div>

              <form onSubmit={handleSendMessage} className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about strategy, market intelligence, siphon logic, risk management..."
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button 
                  type="submit" 
                  disabled={isLoading || !input.trim()}
                  className="gap-2"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
