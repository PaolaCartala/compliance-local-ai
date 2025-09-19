import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Settings } from 'lucide-react';
import { ThreadSidebar } from '@/components/chat/ThreadSidebar';
import { ConversationWindow } from '@/components/chat/ConversationWindow';
import { CustomGPTModal } from '@/components/chat/CustomGPTModal';
import { 
  useThreads, 
  useCustomGPTs, 
  useCreateThread, 
  useSendMessage,
  useUpdateThread,
  useDeleteThread,
  useCreateCustomGPT,
  useUpdateCustomGPT,
  useThreadMessages
} from '@/hooks/useAPI';
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
  
  // Local state
  const [selectedThreadId, setSelectedThreadId] = useState<string>();
  const [selectedCustomGPTId, setSelectedCustomGPTId] = useState<string>('');
  const [isAIThinking, setIsAIThinking] = useState(false);
  const [lastAssistantMessageCount, setLastAssistantMessageCount] = useState(0);
  
  // Modal states
  const [customGPTModalOpen, setCustomGPTModalOpen] = useState(false);
  const [customGPTModalMode, setCustomGPTModalMode] = useState<'create' | 'edit'>('create');
  const [editingCustomGPT, setEditingCustomGPT] = useState<CustomGPT>();

  // API hooks for data fetching
  const { data: threadsData, isLoading: threadsLoading } = useThreads();
  const { data: customGPTsData, isLoading: customGPTsLoading } = useCustomGPTs();
  const { data: threadMessagesData, isLoading: messagesLoading } = useThreadMessages(selectedThreadId);
  
  // Mutations for API operations
  const createThreadMutation = useCreateThread();
  const sendMessageMutation = useSendMessage();
  const updateThreadMutation = useUpdateThread();
  const deleteThreadMutation = useDeleteThread();
  const createCustomGPTMutation = useCreateCustomGPT();
  const updateCustomGPTMutation = useUpdateCustomGPT();

  // Extract data from API responses
  const threads = threadsData?.items || [];
  const customGPTs = customGPTsData?.items || [];
  
  // Set default Custom GPT when data loads
  React.useEffect(() => {
    if (customGPTs.length > 0 && !selectedCustomGPTId) {
      setSelectedCustomGPTId(customGPTs[0].id);
    }
  }, [customGPTs, selectedCustomGPTId]);

  // Get current thread and its messages
  const currentThread = threads.find(t => t.id === selectedThreadId);
  // Sort messages by creation date (oldest first) for proper chat display
  const threadMessages: Message[] = React.useMemo(() => {
    const messages = threadMessagesData?.items || [];
    return [...messages].sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      return dateA.getTime() - dateB.getTime();
    });
  }, [threadMessagesData?.items]);

  // Count assistant messages to detect new AI responses
  const assistantMessageCount = React.useMemo(() => {
    return threadMessages.filter(msg => msg.role === 'assistant').length;
  }, [threadMessages]);

  // Monitor for new assistant messages to stop thinking indicator
  React.useEffect(() => {
    console.log('Chat Debug - Assistant message count changed:', assistantMessageCount, 'Previous:', lastAssistantMessageCount);
    
    if (isAIThinking && assistantMessageCount > lastAssistantMessageCount) {
      console.log('Chat Debug - New AI response detected, stopping thinking indicator');
      setIsAIThinking(false);
      setLastAssistantMessageCount(assistantMessageCount);
    }
  }, [assistantMessageCount, isAIThinking, lastAssistantMessageCount]);

  // Reset thinking state when changing threads
  React.useEffect(() => {
    console.log('Chat Debug - Thread changed, resetting thinking state');
    setIsAIThinking(false);
    setLastAssistantMessageCount(assistantMessageCount);
  }, [selectedThreadId, assistantMessageCount]);
  
  // Debug logging
  React.useEffect(() => {
    console.log('Chat Debug - Selected thread ID:', selectedThreadId);
    console.log('Chat Debug - Thread messages data:', threadMessagesData);
    console.log('Chat Debug - Thread messages count:', threadMessages.length);
    console.log('Chat Debug - Assistant message count:', assistantMessageCount);
    console.log('Chat Debug - Last assistant message count:', lastAssistantMessageCount);
    console.log('Chat Debug - Messages loading:', messagesLoading);
    console.log('Chat Debug - isAIThinking:', isAIThinking);
    if (threadMessages.length > 0) {
      console.log('Chat Debug - First message:', threadMessages[0]);
      console.log('Chat Debug - Last message:', threadMessages[threadMessages.length - 1]);
    }
  }, [selectedThreadId, threadMessagesData, threadMessages, messagesLoading, isAIThinking, assistantMessageCount, lastAssistantMessageCount]);

  // Thread management
  const handleNewThread = () => {
    if (!selectedCustomGPTId) {
      toast({
        title: "Error",
        description: "Please select a Custom GPT first.",
        variant: "destructive",
      });
      return;
    }

    const title = `New Conversation - ${new Date().toLocaleDateString()}`;
    
    createThreadMutation.mutate({
      title,
      customGptId: selectedCustomGPTId,
    }, {
      onSuccess: (response) => {
        setSelectedThreadId(response.data.id);
      },
    });
  };

  const handleThreadSelect = (threadId: string) => {
    setSelectedThreadId(threadId);
    const thread = threads.find(t => t.id === threadId);
    if (thread) {
      setSelectedCustomGPTId(thread.custom_gpt_id || thread.customGPTId);
    }
  };

  const handleEditThread = (threadId: string) => {
    const newTitle = prompt("Enter new thread title:");
    if (newTitle) {
      updateThreadMutation.mutate({
        threadId,
        updates: { title: newTitle },
      });
    }
  };

  const handleArchiveThread = (threadId: string) => {
    updateThreadMutation.mutate({
      threadId,
      updates: { is_archived: true },
    }, {
      onSuccess: () => {
        if (selectedThreadId === threadId) {
          setSelectedThreadId(undefined);
        }
      },
    });
  };

  const handleDeleteThread = (threadId: string) => {
    if (confirm("Are you sure you want to delete this thread? This action cannot be undone.")) {
      deleteThreadMutation.mutate(threadId, {
        onSuccess: () => {
          if (selectedThreadId === threadId) {
            setSelectedThreadId(undefined);
          }
        },
      });
    }
  };

  // Message handling
  const handleSendMessage = (content: string, attachments?: File[]) => {
    if (!selectedThreadId) {
      toast({
        title: "Error",
        description: "Please select or create a thread first.",
        variant: "destructive",
      });
      return;
    }

    console.log('Chat Debug - Sending message, starting thinking indicator');
    console.log('Chat Debug - Current assistant message count:', assistantMessageCount);
    setIsAIThinking(true);
    setLastAssistantMessageCount(assistantMessageCount); // Set baseline count before sending

    sendMessageMutation.mutate({
      content,
      threadId: selectedThreadId,
      customGptId: selectedCustomGPTId,
      files: attachments,
    });
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
      createCustomGPTMutation.mutate({
        name: customGPT.name,
        description: customGPT.description,
        system_prompt: customGPT.systemPrompt,
        specialization: customGPT.specialization,
        color: customGPT.color,
        icon: customGPT.icon,
        mcp_tools_enabled: customGPT.mcpToolsEnabled,
      }, {
        onSuccess: () => {
          setSelectedCustomGPTId(customGPT.id);
          setCustomGPTModalOpen(false);
        },
      });
    } else {
      updateCustomGPTMutation.mutate({
        customGptId: customGPT.id,
        updates: {
          name: customGPT.name,
          description: customGPT.description,
          system_prompt: customGPT.systemPrompt,
          specialization: customGPT.specialization,
          color: customGPT.color,
          icon: customGPT.icon,
          mcp_tools_enabled: customGPT.mcpToolsEnabled,
        },
      }, {
        onSuccess: () => {
          setCustomGPTModalOpen(false);
        },
      });
    }
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
          isAIThinking={isAIThinking}
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