import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { 
  Plus, 
  Search, 
  MoreVertical, 
  Archive, 
  Trash2, 
  Edit3,
  Filter,
  Users,
  TrendingUp,
  Shield,
  Brain,
  Calculator,
  PiggyBank
} from 'lucide-react';
import { Thread, CustomGPT } from '@/types/chat';
import { cn } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '@/components/ui/dropdown-menu';

interface ThreadSidebarProps {
  threads: Thread[];
  customGPTs: CustomGPT[];
  selectedThreadId?: string;
  onThreadSelect: (threadId: string) => void;
  onNewThread: () => void;
  onEditThread: (threadId: string) => void;
  onArchiveThread: (threadId: string) => void;
  onDeleteThread: (threadId: string) => void;
}

const specializationIcons = {
  crm: Users,
  portfolio: TrendingUp,
  compliance: Shield,
  general: Brain,
  retirement: PiggyBank,
  tax: Calculator
};

const specializationColors = {
  crm: 'blue',
  portfolio: 'green', 
  compliance: 'red',
  general: 'purple',
  retirement: 'indigo',
  tax: 'orange'
};

export function ThreadSidebar({
  threads,
  customGPTs,
  selectedThreadId,
  onThreadSelect,
  onNewThread,
  onEditThread,
  onArchiveThread,
  onDeleteThread
}: ThreadSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSpecialization, setFilterSpecialization] = useState<string>('all');

  const getCustomGPTForThread = (thread: Thread) => {
    return customGPTs.find(gpt => gpt.id === thread.customGPTId);
  };

  const filteredThreads = threads.filter(thread => {
    const matchesSearch = thread.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      thread.lastMessage?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const customGPT = getCustomGPTForThread(thread);
    const matchesFilter = filterSpecialization === 'all' || 
      customGPT?.specialization === filterSpecialization;
    
    return matchesSearch && matchesFilter && !thread.isArchived;
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="flex flex-col h-full bg-card border-r">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Chat Threads</h3>
          <Button size="sm" onClick={onNewThread} className="bg-primary hover:bg-primary/90">
            <Plus className="w-4 h-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search threads..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Filter */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Filter className="w-4 h-4 mr-2" />
              {filterSpecialization === 'all' ? 'All Types' : 
                customGPTs.find(gpt => gpt.specialization === filterSpecialization)?.name || 'All Types'
              }
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            <DropdownMenuItem onClick={() => setFilterSpecialization('all')}>
              All Types
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            {customGPTs.map(gpt => {
              const Icon = specializationIcons[gpt.specialization] || Brain;
              return (
                <DropdownMenuItem 
                  key={gpt.id}
                  onClick={() => setFilterSpecialization(gpt.specialization)}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {gpt.name}
                </DropdownMenuItem>
              );
            })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Threads List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-2">
          {filteredThreads.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <div className="text-4xl mb-2">💬</div>
              <p className="text-sm">No threads found</p>
              <p className="text-xs">Start a new conversation</p>
            </div>
          ) : (
            filteredThreads.map(thread => {
              const customGPT = getCustomGPTForThread(thread);
              const Icon = customGPT ? specializationIcons[customGPT.specialization] || Brain : Brain;
              const isSelected = thread.id === selectedThreadId;

              return (
                <Card 
                  key={thread.id}
                  className={cn(
                    "p-3 cursor-pointer transition-colors hover:bg-accent/50",
                    isSelected && "ring-2 ring-primary bg-accent/20"
                  )}
                  onClick={() => onThreadSelect(thread.id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0 overflow-hidden">
                      {/* Header with badge */}
                      <div className="flex items-center gap-2 mb-1">
                        {customGPT && (
                          <Badge 
                            variant="secondary" 
                            className={cn(
                              "text-xs px-1.5 py-0.5",
                              `bg-${specializationColors[customGPT.specialization]}-100 text-${specializationColors[customGPT.specialization]}-700 border-${specializationColors[customGPT.specialization]}-200`
                            )}
                          >
                            <Icon className="w-3 h-3 mr-1" />
                            {customGPT.name}
                          </Badge>
                        )}
                      </div>

                      {/* Thread title */}
                      <h4 className="font-medium text-sm mb-1 break-words leading-tight line-clamp-2">
                        {thread.title}
                      </h4>

                      {/* Last message preview */}
                      {thread.lastMessage && (
                        <p className="text-xs text-muted-foreground mb-2 break-words leading-tight line-clamp-2">
                          {thread.lastMessage}
                        </p>
                      )}

                      {/* Footer info */}
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{thread.messageCount} messages</span>
                        <span>{formatDate(thread.updatedAt)}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-6 w-6 p-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onEditThread(thread.id)}>
                          <Edit3 className="w-4 h-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onArchiveThread(thread.id)}>
                          <Archive className="w-4 h-4 mr-2" />
                          Archive
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => onDeleteThread(thread.id)}
                          className="text-destructive"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      </ScrollArea>
    </div>
  );
}