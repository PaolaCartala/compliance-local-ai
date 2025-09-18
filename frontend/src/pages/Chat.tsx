import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Settings } from 'lucide-react';
import { ThreadSidebar } from '@/components/chat/ThreadSidebar';
import { ConversationWindow } from '@/components/chat/ConversationWindow';
import { CustomGPTModal } from '@/components/chat/CustomGPTModal';
import { 
  mockCustomGPTs as initialCustomGPTs, 
  mockThreads as initialThreads, 
  mockMessages as initialMessages 
} from '@/data/mockChatData';
import { CustomGPT, Thread, Message } from '@/types/chat';
import { useToast } from '@/hooks/use-toast';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function Chat() {
  const { toast } = useToast();
  
  // State management
  const [customGPTs, setCustomGPTs] = useState<CustomGPT[]>(initialCustomGPTs);
  const [threads, setThreads] = useState<Thread[]>(initialThreads);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [selectedThreadId, setSelectedThreadId] = useState<string>();
  const [selectedCustomGPTId, setSelectedCustomGPTId] = useState<string>(customGPTs[0]?.id || '');
  
  // Modal states
  const [customGPTModalOpen, setCustomGPTModalOpen] = useState(false);
  const [customGPTModalMode, setCustomGPTModalMode] = useState<'create' | 'edit'>('create');
  const [editingCustomGPT, setEditingCustomGPT] = useState<CustomGPT>();

  // Get current thread and its messages
  const currentThread = threads.find(t => t.id === selectedThreadId);
  const threadMessages = selectedThreadId 
    ? messages.filter(m => m.threadId === selectedThreadId)
    : [];

  // Thread management
  const handleNewThread = () => {
    const newThread: Thread = {
      id: `thread_${Date.now()}`,
      title: `New Conversation - ${new Date().toLocaleDateString()}`,
      customGPTId: selectedCustomGPTId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messageCount: 0,
      isArchived: false
    };

    setThreads(prev => [newThread, ...prev]);
    setSelectedThreadId(newThread.id);
    
    toast({
      title: "New Thread Created",
      description: "Start your conversation with the selected CustomGPT."
    });
  };

  const handleThreadSelect = (threadId: string) => {
    setSelectedThreadId(threadId);
    const thread = threads.find(t => t.id === threadId);
    if (thread) {
      setSelectedCustomGPTId(thread.customGPTId);
    }
  };

  const handleEditThread = (threadId: string) => {
    // In a real app, this would open a rename dialog
    const newTitle = prompt("Enter new thread title:");
    if (newTitle) {
      setThreads(prev => prev.map(t => 
        t.id === threadId 
          ? { ...t, title: newTitle, updatedAt: new Date().toISOString() }
          : t
      ));
      toast({
        title: "Thread Renamed",
        description: "Thread title updated successfully."
      });
    }
  };

  const handleArchiveThread = (threadId: string) => {
    setThreads(prev => prev.map(t => 
      t.id === threadId 
        ? { ...t, isArchived: true, updatedAt: new Date().toISOString() }
        : t
    ));
    
    if (selectedThreadId === threadId) {
      setSelectedThreadId(undefined);
    }
    
    toast({
      title: "Thread Archived",
      description: "Thread moved to archives."
    });
  };

  const handleDeleteThread = (threadId: string) => {
    if (confirm("Are you sure you want to delete this thread? This action cannot be undone.")) {
      setThreads(prev => prev.filter(t => t.id !== threadId));
      setMessages(prev => prev.filter(m => m.threadId !== threadId));
      
      if (selectedThreadId === threadId) {
        setSelectedThreadId(undefined);
      }
      
      toast({
        title: "Thread Deleted",
        description: "Thread and all messages have been permanently deleted.",
        variant: "destructive"
      });
    }
  };

  // Message handling
  const handleSendMessage = (content: string, attachments?: File[]) => {
    if (!selectedThreadId) return;

    // User message
    const userMessage: Message = {
      id: `msg_${Date.now()}_user`,
      threadId: selectedThreadId,
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
      attachments: attachments?.map(file => ({
        id: `file_${Date.now()}_${file.name}`,
        name: file.name,
        type: file.type,
        size: file.size,
        url: URL.createObjectURL(file),
        uploadedAt: new Date().toISOString()
      }))
    };

    setMessages(prev => [...prev, userMessage]);

    // Update thread
    setThreads(prev => prev.map(t => 
      t.id === selectedThreadId 
        ? { 
            ...t, 
            messageCount: t.messageCount + 1,
            lastMessage: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
            updatedAt: new Date().toISOString() 
          }
        : t
    ));

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: `msg_${Date.now()}_ai`,
        threadId: selectedThreadId,
        content: generateMockAIResponse(content, selectedCustomGPTId),
        role: 'assistant',
        timestamp: new Date().toISOString(),
        customGPTId: selectedCustomGPTId,
        mcpToolInteractions: Math.random() > 0.5 ? [
          {
            toolName: 'redtail-crm',
            action: 'fetch_client_data',
            data: { query: content },
            timestamp: new Date().toISOString(),
            success: true
          }
        ] : undefined
      };

      setMessages(prev => [...prev, aiMessage]);
      setThreads(prev => prev.map(t => 
        t.id === selectedThreadId 
          ? { 
              ...t, 
              messageCount: t.messageCount + 1,
              lastMessage: aiMessage.content.substring(0, 100) + (aiMessage.content.length > 100 ? '...' : ''),
              updatedAt: new Date().toISOString() 
            }
          : t
      ));
    }, 1500);
  };

  // CustomGPT management
  const handleCreateCustomGPT = () => {
    setCustomGPTModalMode('create');
    setEditingCustomGPT(undefined);
    setCustomGPTModalOpen(true);
  };

  const handleEditCustomGPT = (customGPT: CustomGPT) => {
    setCustomGPTModalMode('edit');
    setEditingCustomGPT(customGPT);
    setCustomGPTModalOpen(true);
  };

  const handleSaveCustomGPT = (customGPT: CustomGPT) => {
    if (customGPTModalMode === 'create') {
      setCustomGPTs(prev => [...prev, customGPT]);
      setSelectedCustomGPTId(customGPT.id);
    } else {
      setCustomGPTs(prev => prev.map(gpt => 
        gpt.id === customGPT.id ? customGPT : gpt
      ));
    }
  };

  // Mock AI response generator
  const generateMockAIResponse = (userMessage: string, customGPTId: string): string => {
    const customGPT = customGPTs.find(gpt => gpt.id === customGPTId);
    const responses = {
      crm: "I've accessed the client's profile from Redtail CRM. Based on their interaction history, I can see they last contacted us on...",
      portfolio: "I've analyzed the portfolio data from Albridge. The current allocation shows... I recommend the following adjustments:",
      compliance: "I've reviewed this request for SEC compliance. All recommendations align with regulatory requirements. Documentation has been updated in the audit trail.",
      general: "Based on my comprehensive analysis incorporating both CRM data and portfolio information, here's my recommendation...",
      retirement: "For retirement planning, I've calculated the optimal contribution strategy based on current tax brackets and projected retirement needs...",
      tax: "From a tax efficiency perspective, I recommend the following strategies to minimize your tax liability while maximizing long-term growth..."
    };

    return responses[customGPT?.specialization || 'general'] || "I understand your request. Let me analyze this information and provide you with a comprehensive response...";
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Left Sidebar - Threads */}
      <div className="w-80 border-r">
        <ThreadSidebar
          threads={threads}
          customGPTs={customGPTs}
          selectedThreadId={selectedThreadId}
          onThreadSelect={handleThreadSelect}
          onNewThread={handleNewThread}
          onEditThread={handleEditThread}
          onArchiveThread={handleArchiveThread}
          onDeleteThread={handleDeleteThread}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="border-b p-4 bg-card">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold">SecureChat AI</h1>
            <div className="flex items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4 mr-2" />
                    Manage CustomGPTs
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={handleCreateCustomGPT}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create New CustomGPT
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  {customGPTs.map(gpt => (
                    <DropdownMenuItem 
                      key={gpt.id}
                      onClick={() => handleEditCustomGPT(gpt)}
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Edit {gpt.name}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>

        {/* Conversation Window */}
        <ConversationWindow
          thread={currentThread}
          messages={threadMessages}
          customGPTs={customGPTs}
          selectedCustomGPTId={selectedCustomGPTId}
          onCustomGPTChange={setSelectedCustomGPTId}
          onSendMessage={handleSendMessage}
        />
      </div>

      {/* CustomGPT Management Modal */}
      <CustomGPTModal
        open={customGPTModalOpen}
        onOpenChange={setCustomGPTModalOpen}
        mode={customGPTModalMode}
        customGPT={editingCustomGPT}
        onSave={handleSaveCustomGPT}
      />
    </div>
  );
}