import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { LocationMap } from './LocationMap';
import { chatApi } from '../services/api';
import type { Message } from '../types/chat';
import './Studio.css';

interface StudioProps {
  messages: Message[];
  sessionId?: string;
  isCollapsed?: boolean;
}

type StudioView = 'menu' | 'mindmap' | 'quiz' | 'flashcards' | 'summary' | 'report' | 'analyzemap';

interface StudioOption {
  id: StudioView;
  title: string;
  icon: string;
  description: string;
  color: string;
  beta?: boolean;
}

const studioOptions: StudioOption[] = [
  {
    id: 'mindmap',
    title: 'Location Map',
    icon: '📍',
    description: 'Track knowledge sources and their locations',
    color: '#e9d5ff',
  },
  {
    id: 'analyzemap',
    title: 'MindMap',
    icon: '🧠',
    description: 'Hierarchical curriculum framework analyzer',
    color: '#ddd6fe',
  },
  {
    id: 'summary',
    title: 'Summary',
    icon: '📝',
    description: 'Concise summary of key points',
    color: '#dbeafe',
  },
  {
    id: 'quiz',
    title: 'Quiz',
    icon: '❓',
    description: 'Test your understanding',
    color: '#bfdbfe',
  },
  {
    id: 'flashcards',
    title: 'Flashcards',
    icon: '🎴',
    description: 'Study cards for review',
    color: '#fed7aa',
  },
  {
    id: 'report',
    title: 'Reports',
    icon: '📊',
    description: 'Detailed analysis and insights',
    color: '#fef3c7',
  },
];

export const Studio: React.FC<StudioProps> = ({ messages, sessionId, isCollapsed = false }) => {
  const [currentView, setCurrentView] = useState<StudioView>('menu');
  const [generatedContent, setGeneratedContent] = useState<Record<string, any>>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOptionClick = async (optionId: StudioView) => {
    if (optionId === 'mindmap') {
      setCurrentView('mindmap');
      return;
    }

    if (!sessionId) {
      setError('Please start a conversation first to generate content.');
      return;
    }

    setCurrentView(optionId);
    setIsGenerating(true);
    setError(null);

    try {
      const response = await chatApi.generateStudioContent(sessionId, optionId);

      if (response.success) {
        setGeneratedContent({
          ...generatedContent,
          [optionId]: response.data
        });
      } else {
        setError(response.message || 'Failed to generate content');
      }
    } catch (err: any) {
      console.error('Error generating content:', err);
      setError(err.response?.data?.detail || 'Failed to generate content. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBackToMenu = () => {
    setCurrentView('menu');
    setError(null);
  };

  if (isCollapsed) {
    return null;
  }

  // Show Location Map view
  if (currentView === 'mindmap') {
    console.log('🎨 Studio rendering Location Map with', messages.length, 'messages');
    return (
      <div className="studio-container">
        <div className="studio-header">
          <button className="back-button" onClick={handleBackToMenu}>
            ← Back to Studio
          </button>
        </div>
        <div className="studio-content" style={{ padding: 0, position: 'relative' }}>
          <LocationMap messages={messages} isCollapsed={false} />
        </div>
      </div>
    );
  }

  // Show generated content view
  if (currentView !== 'menu') {
    const option = studioOptions.find(opt => opt.id === currentView);
    const content = generatedContent[currentView];

    return (
      <div className="studio-container">
        <div className="studio-header">
          <button className="back-button" onClick={handleBackToMenu}>
            ← Back to Studio
          </button>
          <h3>{option?.icon} {option?.title}</h3>
        </div>
        <div className="studio-content">
          {isGenerating ? (
            <div className="generating-state">
              <div className="spinner-large"></div>
              <p>Generating {option?.title}...</p>
              <p className="generating-hint">This may take a moment</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h4>Error</h4>
              <p>{error}</p>
              <button className="retry-button" onClick={() => handleOptionClick(currentView)}>
                Try Again
              </button>
            </div>
          ) : content ? (
            <div className="content-display">
              {currentView === 'summary' && <SummaryView data={content} />}
              {currentView === 'quiz' && <QuizView data={content} />}
              {currentView === 'flashcards' && <FlashcardsView data={content} />}
              {currentView === 'report' && <ReportView data={content} />}
              {currentView === 'analyzemap' && <MindMapView data={content} />}
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  // Show Studio menu
  return (
    <div className="studio-container">
      <div className="studio-header">
        <div>
          <h3>🎨 Studio</h3>
          <p className="studio-subtitle">Generate study materials from your conversation</p>
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="studio-empty-state">
          <div className="empty-state-icon">📚</div>
          <h4>Start a conversation first</h4>
          <p>Upload documents and chat to unlock Studio features</p>
        </div>
      ) : (
        <div className="studio-grid">
          {studioOptions.map((option) => (
            <button
              key={option.id}
              className="studio-option"
              style={{ backgroundColor: option.color }}
              onClick={() => handleOptionClick(option.id)}
              disabled={isGenerating}
            >
              <div className="option-icon">{option.icon}</div>
              <div className="option-content">
                <h4>
                  {option.title}
                  {option.beta && <span className="beta-badge">BETA</span>}
                </h4>
                <p>{option.description}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// Summary View Component
const SummaryView: React.FC<{ data: any }> = ({ data }) => (
  <div className="summary-view">
    <ReactMarkdown>{data.content}</ReactMarkdown>
    <div className="metadata">
      <span>📊 Based on {data.message_count} messages</span>
    </div>
  </div>
);

// Quiz View Component
const QuizView: React.FC<{ data: any }> = ({ data }) => {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [showResults, setShowResults] = useState(false);

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    setSelectedAnswers({ ...selectedAnswers, [questionIndex]: answer });
  };

  const handleSubmit = () => {
    setShowResults(true);
  };

  const calculateScore = () => {
    let correct = 0;
    data.questions.forEach((q: any, index: number) => {
      if (selectedAnswers[index] === q.correct_answer) {
        correct++;
      }
    });
    return correct;
  };

  return (
    <div className="quiz-view">
      <div className="quiz-header">
        <h4>📝 Quiz - {data.total_questions} Questions</h4>
        {showResults && (
          <div className="quiz-score">
            Score: {calculateScore()} / {data.total_questions}
          </div>
        )}
      </div>

      {data.questions.map((question: any, index: number) => (
        <div key={index} className={`quiz-question ${showResults ? 'show-results' : ''}`}>
          <div className="question-header">
            <span className="question-number">Question {index + 1}</span>
          </div>
          <p className="question-text">{question.question}</p>

          <div className="options">
            {Object.entries(question.options).map(([key, value]: [string, any]) => {
              const isSelected = selectedAnswers[index] === key;
              const isCorrect = key === question.correct_answer;
              const showCorrect = showResults && isCorrect;
              const showIncorrect = showResults && isSelected && !isCorrect;

              return (
                <button
                  key={key}
                  className={`option ${isSelected ? 'selected' : ''} ${showCorrect ? 'correct' : ''} ${showIncorrect ? 'incorrect' : ''}`}
                  onClick={() => !showResults && handleAnswerSelect(index, key)}
                  disabled={showResults}
                >
                  <span className="option-key">{key}</span>
                  <span className="option-text">{value}</span>
                </button>
              );
            })}
          </div>

          {showResults && (
            <div className="explanation">
              <strong>Explanation:</strong> {question.explanation}
            </div>
          )}
        </div>
      ))}

      <div className="quiz-actions">
        {!showResults ? (
          <button
            className="submit-quiz-button"
            onClick={handleSubmit}
            disabled={Object.keys(selectedAnswers).length < data.total_questions}
          >
            Submit Quiz
          </button>
        ) : (
          <button
            className="retry-quiz-button"
            onClick={() => { setSelectedAnswers({}); setShowResults(false); }}
          >
            Retry Quiz
          </button>
        )}
      </div>
    </div>
  );
};

// Flashcards View Component
const FlashcardsView: React.FC<{ data: any }> = ({ data }) => {
  const [currentCard, setCurrentCard] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const handleNext = () => {
    setCurrentCard((prev) => (prev + 1) % data.total_cards);
    setIsFlipped(false);
  };

  const handlePrevious = () => {
    setCurrentCard((prev) => (prev - 1 + data.total_cards) % data.total_cards);
    setIsFlipped(false);
  };

  // Helper function to clean category text from content
  const cleanContent = (content: string): string => {
    // Remove "Category: XYZ" patterns that appear inline in the text
    return content.replace(/\s*Category:\s*[A-Za-z\s]+\s*/g, ' ').replace(/\s+/g, ' ').trim();
  };

  const card = data.flashcards[currentCard];

  return (
    <div className="flashcards-view">
      <div className="flashcard-header">
        <h4>🎴 Flashcards</h4>
        <span className="card-counter">
          {currentCard + 1} / {data.total_cards}
        </span>
      </div>

      <div
        className={`flashcard ${isFlipped ? 'flipped' : ''}`}
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <div className="flashcard-inner">
          <div className="flashcard-front">
            <div className="card-label">Front</div>
            <div className="card-content">{cleanContent(card.front)}</div>
            <div className="card-hint">Click to flip</div>
          </div>
          <div className="flashcard-back">
            <div className="card-label">Back</div>
            <div className="card-content">{cleanContent(card.back)}</div>
            {card.category && (
              <div className="card-category">Category: {card.category}</div>
            )}
          </div>
        </div>
      </div>

      <div className="flashcard-navigation">
        <button onClick={handlePrevious} disabled={data.total_cards <= 1}>
          ← Previous
        </button>
        <button onClick={handleNext} disabled={data.total_cards <= 1}>
          Next →
        </button>
      </div>
    </div>
  );
};

// Report View Component
const ReportView: React.FC<{ data: any }> = ({ data }) => (
  <div className="report-view">
    <ReactMarkdown>{data.content}</ReactMarkdown>
    <div className="metadata">
      <span>📊 Based on {data.message_count} messages</span>
    </div>
  </div>
);

// MindMap View Component
const MindMapView: React.FC<{ data: any }> = ({ data }) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set([data.root_node?.id || 'root']));
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Pan state
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  // Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) { // Left mouse button
      setIsPanning(true);
      setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      e.preventDefault();
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isPanning) {
      setPan({
        x: e.clientX - startPan.x,
        y: e.clientY - startPan.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  // Add/remove event listeners for panning
  useEffect(() => {
    if (isPanning) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'grabbing';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
    };
  }, [isPanning, startPan]);

  const renderNode = (node: any, level: number, yOffset: number): { element: React.ReactElement; height: number; yPos: number } => {
    const hasChildren = node.subtopics && node.subtopics.length > 0;
    const isExpanded = expandedNodes.has(node.id);
    const isRoot = level === 0;

    let buttonClass = 'map-node-button';
    if (isRoot) buttonClass += ' root-level';
    else if (level === 1) buttonClass += ' level-1';
    else buttonClass += ' level-2';

    let totalHeight = 80;
    let childElements: React.ReactElement[] = [];
    let childPositions: { yPos: number }[] = [];

    if (hasChildren && isExpanded) {
      let currentY = yOffset;
      node.subtopics.forEach((child: any) => {
        const result = renderNode(child, level + 1, currentY);
        childElements.push(result.element);
        childPositions.push({ yPos: result.yPos });
        currentY += result.height + 20;
      });
      totalHeight = currentY - yOffset;
    }

    const xPos = level * 320 + 50;
    const yPos = yOffset + totalHeight / 2;

    return {
      element: (
        <g key={node.id}>
          <foreignObject x={xPos} y={yPos - 25} width="250" height="50">
            <button
              className={buttonClass}
              onClick={(e) => {
                e.stopPropagation();
                if (hasChildren) toggleNode(node.id);
              }}
              onMouseDown={(e) => e.stopPropagation()}
            >
              <span className="node-text">{node.title}</span>
              {hasChildren && (
                <span className="expand-arrow">{isExpanded ? '›' : '›'}</span>
              )}
            </button>
          </foreignObject>
          {childElements}
          {hasChildren && isExpanded && node.subtopics.map((child: any, index: number) => {
            const childY = childPositions[index].yPos;

            const startX = xPos + 250;
            const startY = yPos;
            const endX = xPos + 320;
            const endY = childY;
            const midX = (startX + endX) / 2;

            return (
              <path
                key={`line-${node.id}-${child.id}`}
                d={`M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`}
                stroke="#93c5fd"
                strokeWidth="2"
                fill="none"
                opacity="0.6"
              />
            );
          })}
        </g>
      ),
      height: totalHeight,
      yPos: yPos
    };
  };

  useEffect(() => {
    if (svgRef.current && data.root_node) {
      const calculateHeight = (node: any, level: number): number => {
        if (!node.subtopics || node.subtopics.length === 0 || !expandedNodes.has(node.id)) {
          return 80;
        }
        let total = 0;
        node.subtopics.forEach((child: any) => {
          total += calculateHeight(child, level + 1) + 20;
        });
        return Math.max(80, total);
      };

      const calculateMaxDepth = (node: any, level: number): number => {
        if (!node.subtopics || node.subtopics.length === 0 || !expandedNodes.has(node.id)) {
          return level;
        }
        let maxDepth = level;
        node.subtopics.forEach((child: any) => {
          const childDepth = calculateMaxDepth(child, level + 1);
          maxDepth = Math.max(maxDepth, childDepth);
        });
        return maxDepth;
      };

      const height = calculateHeight(data.root_node, 0);
      const maxDepth = calculateMaxDepth(data.root_node, 0);
      const width = Math.max(1200, (maxDepth + 1) * 320 + 100);

      svgRef.current.style.height = `${Math.max(500, height + 100)}px`;
      svgRef.current.setAttribute('width', width.toString());
    }
  }, [expandedNodes, data.root_node]);

  return (
    <div className="mindmap-view">
      <div className="mindmap-header">
        <h4>{data.title || 'Curriculum Framework'}</h4>
        {data.source_count && (
          <p className="source-info">Basierend auf {data.source_count} Quelle{data.source_count > 1 ? 'n' : ''}</p>
        )}
        <p className="pan-hint" style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.5rem' }}>
          💡 Click and drag to pan, scroll to zoom
        </p>
      </div>
      <div
        ref={containerRef}
        className="mindmap-svg-container"
        onMouseDown={handleMouseDown}
        style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
      >
        <svg ref={svgRef} className="mindmap-svg" width="1200" height="500">
          <g transform={`translate(${pan.x}, ${pan.y})`}>
            {data.root_node && renderNode(data.root_node, 0, 50).element}
          </g>
        </svg>
      </div>
    </div>
  );
};
