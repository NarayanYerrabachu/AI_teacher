import axios from 'axios';
import type { ChatRequest, ChatResponse, UploadResponse } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  // Send a chat message (non-streaming)
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },

  // Stream a chat message (using fetch and ReadableStream)
  streamMessage: (
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onSources: (sources: any[], sessionId: string) => void,
    onError: (error: string) => void,
    onComplete: () => void
  ): (() => void) => {
    const abortController = new AbortController();

    (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('No reader available');
        }

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                switch (data.type) {
                  case 'chunk':
                    onChunk(data.content);
                    break;
                  case 'sources':
                    onSources(data.sources, data.session_id);
                    break;
                  case 'done':
                    onComplete();
                    return;
                  case 'error':
                    onError(data.message);
                    return;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          onError(error.message || 'Connection error');
        }
      }
    })();

    // Return cleanup function
    return () => {
      abortController.abort();
    };
  },

  // Upload PDF files
  uploadPDF: async (files: File[]): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post<UploadResponse>('/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Clear chat session
  clearSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/clear/${sessionId}`);
  },

  // Get chat history
  getHistory: async (sessionId: string): Promise<any> => {
    const response = await api.get(`/chat/history/${sessionId}`);
    return response.data;
  },
};
