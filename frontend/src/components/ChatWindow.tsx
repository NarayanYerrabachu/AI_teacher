import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { chatApi } from '../services/api';
import type { Message, Source } from '../types/chat';
import './ChatWindow.css';

interface ChatWindowProps {
  messages: Message[];
  onMessagesChange: (messages: Message[]) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, onMessagesChange }) => {
  // Use ref to always have the latest messages for functional updates
  const messagesRef = useRef<Message[]>(messages);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const setMessages = (update: Message[] | ((prev: Message[]) => Message[])) => {
    if (typeof update === 'function') {
      const newMessages = update(messagesRef.current);
      onMessagesChange(newMessages);
    } else {
      onMessagesChange(update);
    }
  };
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingMessageRef = useRef<string>('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

  const handleSendMessage = async (message: string) => {
    // Add user message with unique ID
    const userMessage: Message = {
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);
    setCurrentStreamingMessage('');
    streamingMessageRef.current = '';

    // Stream response
    const cleanup = chatApi.streamMessage(
      {
        message,
        session_id: sessionId,
        use_rag: true,  // Use RAG mode - requires documents to be uploaded
      },
      // onChunk
      (chunk: string) => {
        streamingMessageRef.current += chunk;
        setCurrentStreamingMessage((prev) => prev + chunk);
      },
      // onSources
      (sources: Source[], newSessionId: string) => {
        setSessionId(newSessionId);
        // Create assistant message with accumulated content from ref
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: streamingMessageRef.current,
          timestamp: new Date(),
          sources,
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setCurrentStreamingMessage('');
        streamingMessageRef.current = '';
        setIsStreaming(false);
      },
      // onError
      (error: string) => {
        console.error('Streaming error:', error);
        const errorMessage: Message = {
          id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: `Sorry, an error occurred: ${error}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        setCurrentStreamingMessage('');
        streamingMessageRef.current = '';
        setIsStreaming(false);
      },
      // onComplete
      () => {
        // Final cleanup - create message from accumulated content if not already created
        if (streamingMessageRef.current) {
          setMessages((prev) => {
            // Check if message already exists in the CURRENT state
            const alreadyExists = prev.some(m => m.content === streamingMessageRef.current);
            if (alreadyExists) {
              return prev; // Don't add duplicate
            }
            const assistantMessage: Message = {
              id: `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              role: 'assistant',
              content: streamingMessageRef.current,
              timestamp: new Date(),
            };
            return [...prev, assistantMessage];
          });
          setCurrentStreamingMessage('');
          streamingMessageRef.current = '';
        }
        setIsStreaming(false);
      }
    );

    // Store cleanup function for potential cancellation
    return cleanup;
  };

  const handleUploadFiles = async (files: File[]) => {
    setIsLoading(true);
    setUploadStatus('Uploading...');
    try {
      const response = await chatApi.uploadPDF(files);
      setUploadStatus(`✓ Uploaded ${response.details?.files_processed || files.length} file(s)`);
      setTimeout(() => setUploadStatus(''), 3000);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('✗ Upload failed');
      setTimeout(() => setUploadStatus(''), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearSession = async () => {
    if (sessionId) {
      try {
        await chatApi.clearSession(sessionId);
      } catch (error) {
        console.error('Error clearing session:', error);
      }
    }
    setMessages([]);
    setSessionId(undefined);
    setCurrentStreamingMessage('');
    streamingMessageRef.current = '';
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="header-content">
          <h1>🤖 AI Teacher</h1>
          <p className="subtitle">RAG-powered AI Assistant</p>
        </div>
        <div className="header-actions">
          {uploadStatus && (
            <span className={`upload-status ${uploadStatus.includes('✓') ? 'success' : 'error'}`}>
              {uploadStatus}
            </span>
          )}
          <button
            className="clear-button"
            onClick={handleClearSession}
            disabled={messages.length === 0}
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && !currentStreamingMessage && (
          <div className="welcome-message">
            <h2>👋 Welcome!</h2>
            <p>Upload PDF files and ask questions about them.</p>
            <p className="hint">💡 Click the 📎 button to upload documents</p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Show streaming message */}
        {currentStreamingMessage && (
          <div className="message-container assistant-message">
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-role">AI Assistant</span>
                <span className="streaming-indicator">●</span>
              </div>
              <div className="message-content">
                <p>{currentStreamingMessage}</p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSendMessage={handleSendMessage}
        onUploadFiles={handleUploadFiles}
        disabled={isLoading || isStreaming}
      />
    </div>
  );
};
