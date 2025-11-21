import { useState } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { MindMap } from './components/MindMap';
import type { Message } from './types/chat';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isMindMapCollapsed, setIsMindMapCollapsed] = useState(false);

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
      >
        {isMindMapCollapsed ? '◀' : '▶'}
      </button>
      <div className={`mindmap-section ${isMindMapCollapsed ? 'collapsed' : ''}`}>
        <MindMap messages={messages} isCollapsed={isMindMapCollapsed} />
      </div>
    </div>
  );
}

export default App;
