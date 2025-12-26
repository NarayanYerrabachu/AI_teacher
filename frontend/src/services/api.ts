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
    onSources: (sources: any[], sessionId: string, explanationData?: any) => void,
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

        let buffer = ''; // Buffer for incomplete lines

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Add new chunk to buffer
          buffer += decoder.decode(value, { stream: true });

          // Split by newlines to find complete lines
          const lines = buffer.split('\n');

          // Keep the last (potentially incomplete) line in the buffer
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue; // Skip empty data lines

                const data = JSON.parse(jsonStr);

                switch (data.type) {
                  case 'chunk':
                    onChunk(data.content);
                    break;
                  case 'sources':
                    // Extract the sources array and explanation data from the nested structure
                    console.log('📡 API received sources data:', {
                      hasExplanationAnimation: !!data.sources.explanation_animation,
                      hasExplanationAudio: !!data.sources.explanation_audio,
                      explanationDuration: data.sources.explanation_duration,
                      hasAvatarVideo: !!data.sources.avatar_video_url,
                      sourcesKeys: Object.keys(data.sources)
                    });

                    const explanationData = {
                      animation: data.sources.explanation_animation,
                      audio: data.sources.explanation_audio,
                      duration: data.sources.explanation_duration,
                      avatarVideoUrl: data.sources.avatar_video_url,
                      avatarVideoId: data.sources.avatar_video_id
                    };

                    console.log('📡 Extracted explanationData:', {
                      hasAnimation: !!explanationData.animation,
                      hasAudio: !!explanationData.audio,
                      hasAvatarVideo: !!explanationData.avatarVideoUrl,
                      animationSteps: explanationData.animation?.steps?.length
                    });

                    onSources(
                      data.sources.sources || data.sources,
                      data.session_id,
                      explanationData
                    );
                    break;
                  case 'done':
                    onComplete();
                    return;
                  case 'error':
                    onError(data.message);
                    return;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e, 'Line:', line);
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

  // Generate Studio content
  generateStudioContent: async (sessionId: string, contentType: string): Promise<any> => {
    const response = await api.post('/studio/generate', {
      session_id: sessionId,
      content_type: contentType
    });
    return response.data;
  },

  // Generate explanation on-demand
  generateExplanation: async (message: string, answer: string): Promise<any> => {
    const response = await api.post('/explanation/generate', {
      message,
      answer
    });
    return response.data;
  },
};
