import { useState, useCallback, useRef, useEffect } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { Studio } from './components/Studio';
import type { Message } from './types/chat';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [isStudioCollapsed, setIsStudioCollapsed] = useState(false);
  const [studioWidth, setStudioWidth] = useState(50); // percentage - increased for video content
  const [isDragging, setIsDragging] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(50);
  const collapseButtonRef = useRef<HTMLButtonElement>(null);
  const studioSectionRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (isStudioCollapsed) return;
    setIsDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = studioWidth;
    e.preventDefault();
  }, [isStudioCollapsed, studioWidth]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging) return;

    const windowWidth = window.innerWidth;
    const deltaX = dragStartX.current - e.clientX;
    const deltaPercent = (deltaX / windowWidth) * 100;

    // Calculate new width with constraints (min 25%, max 60%)
    const newWidth = Math.min(60, Math.max(25, dragStartWidth.current + deltaPercent));

    // Update state
    setStudioWidth(newWidth);

    // Directly update DOM for immediate visual feedback during dragging
    if (studioSectionRef.current) {
      studioSectionRef.current.style.width = `${newWidth}%`;
    }
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Add global mouse event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Debug logging
  useEffect(() => {
    console.log('🔧 Studio state:', { isStudioCollapsed, studioWidth });
  }, [isStudioCollapsed, studioWidth]);

  return (
    <div className="app-container">
      <div className={`chat-section ${isStudioCollapsed ? 'full-width' : ''}`}>
        <ChatWindow
          onMessagesChange={setMessages}
          messages={messages}
          onSessionIdChange={setSessionId}
        />
      </div>
      {!isStudioCollapsed && (
        <div
          className="resize-handle"
          onMouseDown={handleMouseDown}
          title="Drag to resize"
          style={{ right: `${studioWidth}%` }}
        />
      )}
      <div
        ref={studioSectionRef}
        className={`studio-section ${isStudioCollapsed ? 'collapsed' : ''} ${isDragging ? 'dragging' : ''}`}
        style={!isStudioCollapsed ? { width: `${studioWidth}%` } : undefined}
      >
        <button
          ref={collapseButtonRef}
          className={`collapse-toggle ${isStudioCollapsed ? 'collapsed-btn' : 'expanded-btn'} ${isDragging ? 'dragging' : ''}`}
          onClick={() => {
            console.log('🔄 Toggle clicked! Current:', isStudioCollapsed, '→ New:', !isStudioCollapsed);
            setIsStudioCollapsed(!isStudioCollapsed);
          }}
          title={isStudioCollapsed ? 'Show Studio' : 'Hide Studio'}
        >
          {isStudioCollapsed ? '◀' : '▶'}
        </button>
        <Studio messages={messages} sessionId={sessionId} isCollapsed={isStudioCollapsed} />
      </div>
    </div>
  );
}

export default App;
