import React, { useMemo, useCallback } from 'react';
import {
  ReactFlow,
  type Edge,
  type ReactFlowInstance,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { Message } from '../types/chat';
import './MindMap.css';

interface MindMapProps {
  messages: Message[];
  isCollapsed?: boolean;
}

interface MindMapNode {
  id: string;
  type?: string;
  data: { label: string; description?: string };
  position: { x: number; y: number };
  style?: React.CSSProperties;
  sourcePosition?: Position;
  targetPosition?: Position;
}

export const MindMap: React.FC<MindMapProps> = ({ messages, isCollapsed = false }) => {
  // Generate nodes and edges from messages
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const nodes: MindMapNode[] = [];
    const edges: Edge[] = [];

    if (messages.length === 0) {
      // Default empty state node
      nodes.push({
        id: 'root',
        type: 'input',
        data: { label: '💭 Conversation Map', description: 'Start chatting to see the map' },
        position: { x: 250, y: 50 },
        style: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          padding: '20px',
          fontSize: '16px',
          fontWeight: 'bold',
          width: 200,
        },
        sourcePosition: Position.Bottom,
      });
      return { nodes, edges };
    }

    // Create root node
    nodes.push({
      id: 'root',
      type: 'input',
      data: { label: '💭 Conversation', description: `${messages.length} messages` },
      position: { x: 250, y: 50 },
      style: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        padding: '16px',
        fontSize: '14px',
        fontWeight: 'bold',
        width: 180,
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    });

    // Track topics with their specific sources
    const topicsWithSources = new Map<string, Map<string, { content: string; pages: Set<number> }>>();
    let currentTopic: string | null = null;

    let yOffset = 180;
    const xSpacing = 280;

    // Process messages to extract topics and their specific sources
    messages.forEach((message) => {
      if (message.role === 'user') {
        // Extract topic from user question (first sentence or 50 chars)
        currentTopic = message.content.slice(0, 50).split(/[.!?]/)[0].trim();
        if (currentTopic && !topicsWithSources.has(currentTopic)) {
          topicsWithSources.set(currentTopic, new Map());
        }
      }

      // Collect sources for the current topic
      if (message.role === 'assistant' && currentTopic && message.sources && message.sources.length > 0) {
        const topicSources = topicsWithSources.get(currentTopic)!;
        message.sources.forEach(source => {
          const sourceKey = source.metadata.source;
          if (!topicSources.has(sourceKey)) {
            topicSources.set(sourceKey, {
              content: source.content.slice(0, 100),
              pages: new Set()
            });
          }
          if (source.metadata.page) {
            topicSources.get(sourceKey)!.pages.add(source.metadata.page);
          }
        });
      }
    });

    // Create topic nodes and their specific source nodes
    const topicArray = Array.from(topicsWithSources.entries());
    let sourceNodeIndex = 0;

    topicArray.forEach(([topic, topicSources], topicIndex) => {
      const topicNodeId = `topic-${topicIndex}`;
      const topicX = (topicIndex % 2) * xSpacing;
      const topicY = yOffset + Math.floor(topicIndex / 2) * 180;

      // Create topic node
      nodes.push({
        id: topicNodeId,
        data: { label: `❓ ${topic}` },
        position: { x: topicX, y: topicY },
        style: {
          background: '#ffffff',
          border: '2px solid #667eea',
          borderRadius: '8px',
          padding: '12px',
          fontSize: '12px',
          width: 220,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      });

      // Connect topic to root
      edges.push({
        id: `root-${topicNodeId}`,
        source: 'root',
        target: topicNodeId,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#667eea', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#667eea' },
      });

      // Create source nodes for this specific topic
      const sourceArray = Array.from(topicSources.entries());
      sourceArray.forEach(([sourceKey, sourceData], sourceIdx) => {
        const sourceNodeId = `source-${sourceNodeIndex++}`;
        const sourceX = topicX + (sourceIdx % 2) * 140 - 70;
        const sourceY = topicY + 100;

        const fileName = sourceKey.split('/').pop() || sourceKey;
        const pageInfo = sourceData.pages.size > 0
          ? ` (pg ${Array.from(sourceData.pages).sort((a, b) => a - b).join(', ')})`
          : '';

        // Create source node
        nodes.push({
          id: sourceNodeId,
          type: 'output',
          data: { label: `📄 ${fileName}${pageInfo}` },
          position: { x: sourceX, y: sourceY },
          style: {
            background: '#f0f4ff',
            border: '2px solid #a5b4fc',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '11px',
            width: 180,
            boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
          },
          targetPosition: Position.Top,
        });

        // Connect this source to its specific topic
        edges.push({
          id: `${topicNodeId}-${sourceNodeId}`,
          source: topicNodeId,
          target: sourceNodeId,
          type: 'smoothstep',
          animated: false,
          style: { stroke: '#a5b4fc', strokeWidth: 1.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#a5b4fc' },
        });
      });
    });

    return { nodes, edges };
  }, [messages]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [hasInitialFit, setHasInitialFit] = React.useState(false);
  const reactFlowInstanceRef = React.useRef<ReactFlowInstance | null>(null);

  // Handle ReactFlow initialization - fit view only once
  const onInit = useCallback((instance: ReactFlowInstance) => {
    reactFlowInstanceRef.current = instance;
    if (!hasInitialFit && initialNodes.length > 0) {
      setTimeout(() => {
        instance.fitView({ padding: 0.2 });
        setHasInitialFit(true);
      }, 0);
    }
  }, [hasInitialFit, initialNodes.length]);

  // Update nodes when messages change
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  if (isCollapsed) {
    return null;
  }

  return (
    <div className="mindmap-container">
      <div className="mindmap-header">
        <h3>🗺️ Knowledge Map</h3>
        <span className="mindmap-subtitle">Visual overview of your conversation</span>
      </div>
      <div className="mindmap-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onInit={onInit}
          attributionPosition="bottom-left"
          minZoom={0.5}
          maxZoom={1.5}
        >
          <Background color="#f0f4ff" gap={16} />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(node) => {
              if (node.type === 'input') return '#667eea';
              if (node.type === 'output') return '#a5b4fc';
              return '#ffffff';
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
            style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
            }}
          />
        </ReactFlow>
      </div>
    </div>
  );
};
