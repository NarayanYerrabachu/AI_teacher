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
      <div className={`mindmap-section ${isMindMapCollapsed ? 'collapsed' : ''}`}>
        <button
          className="collapse-toggle"
          onClick={() => setIsMindMapCollapsed(!isMindMapCollapsed)}
          title={isMindMapCollapsed ? 'Show Mind Map' : 'Hide Mind Map'}
        >
          {isMindMapCollapsed ? '◀' : '▶'}
        </button>
        <MindMap messages={messages} isCollapsed={isMindMapCollapsed} />
      </div>
    </div>
  );
}

export default App;
