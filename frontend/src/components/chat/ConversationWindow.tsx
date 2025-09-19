import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { 
  Send, 
  Paperclip, 
  Download,
  Users,
  TrendingUp,
  Shield,
  Brain,
  Calculator,
  PiggyBank,
  ChevronDown,
  Bot,
  User
} from 'lucide-react';
import { Message, CustomGPT, Thread } from '@/types/chat';
import { cn } from '@/lib/utils';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ComplianceStatus } from '@/components/ComplianceStatus';

interface ConversationWindowProps {
  thread?: Thread;
  messages: Message[];
  customGPTs: CustomGPT[];
  selectedCustomGPTId: string;
  isAIThinking?: boolean;
  onCustomGPTChange: (customGPTId: string) => void;
  onSendMessage: (content: string, attachments?: File[]) => void;
}

const specializationIcons = {
  crm: Users,
  portfolio: TrendingUp,
  compliance: Shield,
  general: Brain,
  retirement: PiggyBank,
  tax: Calculator
};

export function ConversationWindow({
  thread,
  messages,
  customGPTs,
  selectedCustomGPTId,
  isAIThinking = false,
  onCustomGPTChange,
  onSendMessage
}: ConversationWindowProps) {
  const [messageInput, setMessageInput] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const selectedCustomGPT = customGPTs.find(gpt => gpt.id === selectedCustomGPTId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Debug logging for thinking indicator
  useEffect(() => {
    console.log('ConversationWindow Debug - isAIThinking:', isAIThinking);
  }, [isAIThinking]);

  const handleSendMessage = () => {
    if (!messageInput.trim() && attachments.length === 0) return;

    onSendMessage(messageInput, attachments);
    setMessageInput('');
    setAttachments([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments(prev => [...prev, ...newFiles]);
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (timestamp: string) => {
    try {
      // Handle both formats: with and without microseconds
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        console.error('Invalid timestamp:', timestamp);
        return 'Invalid date';
      }
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      console.error('Error formatting timestamp:', timestamp, error);
      return 'Invalid date';
    }
  };

  if (!thread) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-subtle">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-6xl">💬</div>
          <h3 className="text-xl font-semibold">Welcome to SecureChat AI</h3>
          <p className="text-muted-foreground">
            Select an existing thread or start a new conversation with one of your CustomGPT assistants.
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <Shield className="w-4 h-4" />
            <span>SEC-Compliant • Audit Trail Enabled</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* Header */}
      <div className="border-b p-4 bg-card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-lg">{thread.title}</h2>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
              <span>{messages.length} messages</span>
              <span>•</span>
              <span>Last activity: {formatTime(thread.updated_at)}</span>
              {thread.tags && thread.tags.length > 0 && (
                <>
                  <span>•</span>
                  <div className="flex gap-1">
                    {thread.tags.map(tag => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
          
          {/* CustomGPT Selector */}
          <div className="flex items-center gap-3">
            <ComplianceStatus status="secure" size="sm" />
            <Select value={selectedCustomGPTId} onValueChange={onCustomGPTChange}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {customGPTs.map(gpt => {
                  const Icon = specializationIcons[gpt.specialization] || Brain;
                  return (
                    <SelectItem key={gpt.id} value={gpt.id}>
                      <div className="flex items-center gap-2">
                        <Icon className="w-4 h-4" />
                        <span>{gpt.name}</span>
                        {!gpt.isActive && <Badge variant="secondary" className="text-xs">Inactive</Badge>}
                      </div>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4 max-w-4xl mx-auto">
          {messages.map((message) => {
            const messageCustomGPT = customGPTs.find(gpt => gpt.id === (message.custom_gpt_id || message.customGPTId));
            const Icon = message.role === 'user' ? User : 
              (messageCustomGPT ? specializationIcons[messageCustomGPT.specialization] || Bot : Bot);

            return (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Icon className="w-4 h-4 text-primary" />
                  </div>
                )}

                <Card className={cn(
                  "max-w-2xl p-4",
                  message.role === 'user' 
                    ? "bg-primary text-primary-foreground ml-12" 
                    : "bg-card"
                )}>
                  {/* Message header for assistant */}
                  {message.role === 'assistant' && messageCustomGPT && (
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b">
                      <Badge variant="secondary" className="text-xs">
                        <Icon className="w-3 h-3 mr-1" />
                        {messageCustomGPT.name}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatTime(message.created_at)}
                      </span>
                    </div>
                  )}

                  {/* Message content */}
                  <div className="prose prose-sm max-w-none">
                    {message.content.split('\n').map((line, index) => (
                      <p key={index} className={message.role === 'user' ? 'text-primary-foreground' : ''}>
                        {line}
                      </p>
                    ))}
                  </div>

                  {/* Attachments */}
                  {message.attachments && message.attachments.length > 0 && (
                    <div className="mt-3 pt-3 border-t space-y-2">
                      {message.attachments.map((attachment) => (
                        <div key={attachment.id} className="flex items-center gap-2 text-sm">
                          <Paperclip className="w-4 h-4" />
                          <span className="flex-1 truncate">{attachment.name}</span>
                          <span className="text-xs text-muted-foreground">
                            {formatFileSize(attachment.size)}
                          </span>
                          <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                            <Download className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* MCP Tool Interactions */}
                  {message.mcpToolInteractions && message.mcpToolInteractions.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="text-xs text-muted-foreground mb-2">Tool Interactions:</div>
                      {message.mcpToolInteractions.map((interaction, index) => (
                        <Badge key={index} variant="outline" className="text-xs mr-1 mb-1">
                          {interaction.toolName}: {interaction.action}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Compliance flags */}
                  {message.complianceFlags && message.complianceFlags.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="flex items-center gap-2">
                        <Shield className="w-4 h-4 text-warning" />
                        <span className="text-xs text-warning">Compliance Review Required</span>
                      </div>
                    </div>
                  )}

                  {/* Timestamp for user messages */}
                  {message.role === 'user' && (
                    <div className="text-xs text-primary-foreground/70 mt-2">
                      {formatTime(message.created_at)}
                    </div>
                  )}
                </Card>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                    <User className="w-4 h-4 text-secondary-foreground" />
                  </div>
                )}
              </div>
            );
          })}

          {/* AI Thinking indicator */}
          {isAIThinking && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="w-4 h-4 text-primary animate-pulse" />
              </div>
              <Card className="bg-card p-4">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm">{selectedCustomGPT?.name || 'AI Assistant'} is thinking...</span>
                </div>
              </Card>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t p-4 bg-card">
        <div className="max-w-4xl mx-auto">
          {/* Attachments preview */}
          {attachments.length > 0 && (
            <div className="mb-3 space-y-2">
              {attachments.map((file, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-accent/50 rounded text-sm">
                  <Paperclip className="w-4 h-4" />
                  <span className="flex-1 truncate">{file.name}</span>
                  <span className="text-xs text-muted-foreground">{formatFileSize(file.size)}</span>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="h-6 w-6 p-0"
                    onClick={() => removeAttachment(index)}
                  >
                    ×
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Message ${selectedCustomGPT?.name || 'AI Assistant'}...`}
                className="min-h-[60px] max-h-32 resize-none pr-12"
                rows={2}
              />
              <Button
                size="sm"
                variant="ghost"
                className="absolute bottom-2 right-2 h-8 w-8 p-0"
                onClick={() => fileInputRef.current?.click()}
              >
                <Paperclip className="w-4 h-4" />
              </Button>
            </div>
            <Button 
              onClick={handleSendMessage}
              disabled={!messageInput.trim() && attachments.length === 0}
              className="h-[60px] px-6"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.xlsx,.xls"
            className="hidden"
            onChange={handleFileSelect}
          />

          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <div className="flex items-center gap-2">
              <Shield className="w-3 h-3" />
              <span>All conversations are SEC-compliant and audit-logged</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}