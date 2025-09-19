/**
 * React hooks for API data management using React Query
 * 
 * Provides caching, background updates, and error handling
 * for all chat and Custom GPT operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatAPI, customGPTAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Query Keys for React Query
export const QUERY_KEYS = {
  THREADS: ['threads'],
  THREAD_MESSAGES: (threadId: string) => ['thread-messages', threadId],
  CUSTOM_GPTS: ['custom-gpts'],
} as const;

/**
 * Hook for managing user threads
 */
export function useThreads(limit: number = 20, offset: number = 0) {
  return useQuery({
    queryKey: [...QUERY_KEYS.THREADS, limit, offset],
    queryFn: () => chatAPI.getUserThreads(limit, offset),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}

/**
 * Hook for managing thread messages with polling for real-time updates
 */
export function useThreadMessages(
  threadId: string | undefined,
  limit: number = 50,
  offset: number = 0
) {
  return useQuery({
    queryKey: QUERY_KEYS.THREAD_MESSAGES(threadId || ''),
    queryFn: () => {
      if (!threadId) throw new Error('Thread ID is required');
      return chatAPI.getThreadMessages(threadId, limit, offset);
    },
    enabled: !!threadId,
    staleTime: 0, // Always consider data stale to enable frequent refetching
    refetchInterval: 2000, // Poll every 2 seconds when component is focused
    refetchIntervalInBackground: false, // Don't poll in background
    retry: 2,
  });
}

/**
 * Hook for managing Custom GPTs
 */
export function useCustomGPTs(limit: number = 20, offset: number = 0) {
  return useQuery({
    queryKey: [...QUERY_KEYS.CUSTOM_GPTS, limit, offset],
    queryFn: () => customGPTAPI.getCustomGPTs(limit, offset),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
  });
}

/**
 * Mutation hook for creating new threads
 */
export function useCreateThread() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ title, customGptId }: { title: string; customGptId: string }) =>
      chatAPI.createThread(title, customGptId),
    onSuccess: (data) => {
      // Invalidate threads query to refetch
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.THREADS });
      toast({
        title: "Thread Created",
        description: "New conversation thread created successfully.",
      });
    },
    onError: (error) => {
      console.error('Failed to create thread:', error);
      toast({
        title: "Error",
        description: "Failed to create thread. Please try again.",
        variant: "destructive",
      });
    },
  });
}

/**
 * Mutation hook for sending messages
 */
export function useSendMessage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      content,
      threadId,
      customGptId,
      files,
    }: {
      content: string;
      threadId: string;
      customGptId?: string;
      files?: File[];
    }) => chatAPI.sendMessage(content, threadId, customGptId, files),
    onSuccess: (data, variables) => {
      console.log('Message sent successfully, response:', data);
      
      // Immediately invalidate and refetch thread messages
      queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.THREAD_MESSAGES(variables.threadId),
      });
      
      // Force refetch thread messages after a short delay to get the user message
      setTimeout(() => {
        queryClient.refetchQueries({
          queryKey: QUERY_KEYS.THREAD_MESSAGES(variables.threadId),
        });
      }, 500);
      
      // Also invalidate threads to update last message
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.THREADS });
      
      // No toast needed - using visual thinking indicator instead
      // toast({
      //   title: "Message Sent",
      //   description: "Your message has been sent and is being processed.",
      // });
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    },
  });
}

/**
 * Mutation hook for updating threads
 */
export function useUpdateThread() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      threadId,
      updates,
    }: {
      threadId: string;
      updates: { title?: string; is_archived?: boolean };
    }) => chatAPI.updateThread(threadId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.THREADS });
      toast({
        title: "Thread Updated",
        description: "Thread updated successfully.",
      });
    },
    onError: (error) => {
      console.error('Failed to update thread:', error);
      toast({
        title: "Error",
        description: "Failed to update thread. Please try again.",
        variant: "destructive",
      });
    },
  });
}

/**
 * Mutation hook for deleting threads
 */
export function useDeleteThread() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (threadId: string) => chatAPI.deleteThread(threadId),
    onMutate: async (threadId: string) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: QUERY_KEYS.THREADS });
      
      // Snapshot the previous value
      const previousThreads = queryClient.getQueryData(QUERY_KEYS.THREADS);
      
      // Optimistically update to the new value
      queryClient.setQueryData(QUERY_KEYS.THREADS, (oldData: unknown) => {
        const typedOldData = oldData as { items?: Array<{ id: string }>, total?: number } | undefined;
        if (!typedOldData?.items) return typedOldData;
        return {
          ...typedOldData,
          items: typedOldData.items.filter((thread) => thread.id !== threadId),
          total: (typedOldData.total || 0) - 1,
        };
      });
      
      // Return a context object with the snapshotted value
      return { previousThreads };
    },
    onSuccess: (_, threadId) => {
      // Remove thread messages from cache
      queryClient.removeQueries({ queryKey: QUERY_KEYS.THREAD_MESSAGES(threadId) });
      
      toast({
        title: "Thread Deleted",
        description: "Thread deleted successfully.",
      });
    },
    onError: (error, threadId, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousThreads) {
        queryClient.setQueryData(QUERY_KEYS.THREADS, context.previousThreads);
      }
      
      console.error('Failed to delete thread:', error);
      toast({
        title: "Error",
        description: "Failed to delete thread. Please try again.",
        variant: "destructive",
      });
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.THREADS });
    },
  });
}

/**
 * Mutation hook for creating Custom GPTs
 */
export function useCreateCustomGPT() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (customGPTData: {
      name: string;
      description: string;
      system_prompt: string;
      specialization: string;
      color?: string;
      icon?: string;
      mcp_tools_enabled?: {
        redtail_crm: boolean;
        albridge_portfolio: boolean;
        black_diamond: boolean;
      };
    }) => customGPTAPI.createCustomGPT(customGPTData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CUSTOM_GPTS });
      toast({
        title: "Custom GPT Created",
        description: "New Custom GPT created successfully.",
      });
    },
    onError: (error) => {
      console.error('Failed to create Custom GPT:', error);
      toast({
        title: "Error",
        description: "Failed to create Custom GPT. Please try again.",
        variant: "destructive",
      });
    },
  });
}

/**
 * Mutation hook for updating Custom GPTs
 */
export function useUpdateCustomGPT() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      customGptId,
      updates,
    }: {
      customGptId: string;
      updates: Partial<{
        name: string;
        description: string;
        system_prompt: string;
        specialization: string;
        color: string;
        icon: string;
        mcp_tools_enabled: {
          redtail_crm: boolean;
          albridge_portfolio: boolean;
          black_diamond: boolean;
        };
        is_active: boolean;
      }>;
    }) => customGPTAPI.updateCustomGPT(customGptId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CUSTOM_GPTS });
      toast({
        title: "Custom GPT Updated",
        description: "Custom GPT updated successfully.",
      });
    },
    onError: (error) => {
      console.error('Failed to update Custom GPT:', error);
      toast({
        title: "Error",
        description: "Failed to update Custom GPT. Please try again.",
        variant: "destructive",
      });
    },
  });
}