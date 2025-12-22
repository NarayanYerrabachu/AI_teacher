import { useState, useCallback, useRef, useEffect } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { MindMap } from './components/MindMap';
import type { Message } from './types/chat';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isMindMapCollapsed, setIsMindMapCollapsed] = useState(false);
  const [mindMapWidth, setMindMapWidth] = useState(40); // percentage
  const [isDragging, setIsDragging] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(40);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (isMindMapCollapsed) return;
    setIsDragging(true);
    dragStartX.current = e.clientX;
    dragStartWidth.current = mindMapWidth;
    e.preventDefault();
  }, [isMindMapCollapsed, mindMapWidth]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging) return;

    const windowWidth = window.innerWidth;
    const deltaX = dragStartX.current - e.clientX;
    const deltaPercent = (deltaX / windowWidth) * 100;

    // Calculate new width with constraints (min 25%, max 60%)
    const newWidth = Math.min(60, Math.max(25, dragStartWidth.current + deltaPercent));
    setMindMapWidth(newWidth);
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

  return (
    <div className="app-container">
      <div className={`chat-section ${isMindMapCollapsed ? 'full-width' : ''}`}>
        <ChatWindow
          onMessagesChange={setMessages}
          messages={messages}
        />
      </div>
      <button
        className={`collapse-toggle ${isMindMapCollapsed ? 'collapsed-btn' : 'expanded-btn'}`}
        onClick={() => setIsMindMapCollapsed(!isMindMapCollapsed)}
        title={isMindMapCollapsed ? 'Show Mind Map' : 'Hide Mind Map'}
        style={!isMindMapCollapsed ? { right: `calc(${mindMapWidth}% - 32px)` } : undefined}
      >
        {isMindMapCollapsed ? '◀' : '▶'}
      </button>
      {!isMindMapCollapsed && (
        <div
          className="resize-handle"
          onMouseDown={handleMouseDown}
          title="Drag to resize"
          style={{ right: `${mindMapWidth}%` }}
        />
      )}
      <div
        className={`mindmap-section ${isMindMapCollapsed ? 'collapsed' : ''}`}
        style={!isMindMapCollapsed ? { width: `${mindMapWidth}%` } : undefined}
      >
        <MindMap messages={messages} isCollapsed={isMindMapCollapsed} />
      </div>
    </div>
  );
}

export default App;
