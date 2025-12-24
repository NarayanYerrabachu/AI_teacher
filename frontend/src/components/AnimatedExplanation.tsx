import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import type { AnimationData } from '../types/chat';
import './AnimatedExplanation.css';

interface AnimatedExplanationProps {
  animation: AnimationData;
  audioBase64: string;
  avatarVideoUrl?: string; // Optional HeyGen avatar video URL
}

export const AnimatedExplanation: React.FC<AnimatedExplanationProps> = ({
  animation,
  audioBase64,
  avatarVideoUrl,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [visibleSteps, setVisibleSteps] = useState<Set<number>>(new Set());
  const audioRef = useRef<HTMLAudioElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Convert base64 to audio URL
  const audioUrl = `data:audio/mp3;base64,${audioBase64}`;

  // Update current time while playing
  useEffect(() => {
    if (isPlaying && audioRef.current) {
      const updateTime = () => {
        if (audioRef.current) {
          setCurrentTime(audioRef.current.currentTime);
          animationFrameRef.current = requestAnimationFrame(updateTime);
        }
      };
      animationFrameRef.current = requestAnimationFrame(updateTime);
    }

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying]);

  // Update visible steps based on current time
  useEffect(() => {
    const newVisibleSteps = new Set<number>();
    animation.steps.forEach((step, index) => {
      if (currentTime >= step.startTime) {
        newVisibleSteps.add(index);
      }
    });
    setVisibleSteps(newVisibleSteps);
  }, [currentTime, animation.steps]);

  const handlePlay = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleRestart = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      setCurrentTime(0);
      setVisibleSteps(new Set());
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  const getAnimationVariants = (animationType: string) => {
    switch (animationType) {
      case 'fadeIn':
        return {
          hidden: { opacity: 0 },
          visible: { opacity: 1 },
        };
      case 'slideIn':
        return {
          hidden: { opacity: 0, x: -50 },
          visible: { opacity: 1, x: 0 },
        };
      case 'highlight':
        return {
          hidden: { opacity: 0, backgroundColor: 'transparent' },
          visible: {
            opacity: 1,
            backgroundColor: ['transparent', '#ffd70022', 'transparent'],
          },
        };
      case 'scale':
        return {
          hidden: { opacity: 0, scale: 0.8 },
          visible: { opacity: 1, scale: 1 },
        };
      case 'pulse':
        return {
          hidden: { opacity: 0 },
          visible: {
            opacity: 1,
            scale: [1, 1.05, 1],
          },
        };
      default:
        return {
          hidden: { opacity: 0 },
          visible: { opacity: 1 },
        };
    }
  };

  return (
    <div className="animated-explanation">
      <audio
        ref={audioRef}
        src={audioUrl}
        onEnded={handleEnded}
        preload="auto"
      />

      <div className="explanation-header">
        <h3>🎬 {avatarVideoUrl ? 'Avatar Explanation' : 'Animated Explanation'}</h3>
        <div className="explanation-controls">
          {!isPlaying ? (
            <button
              className="control-btn play-btn"
              onClick={handlePlay}
              title="Play explanation"
            >
              ▶️ Play
            </button>
          ) : (
            <button
              className="control-btn pause-btn"
              onClick={handlePause}
              title="Pause explanation"
            >
              ⏸️ Pause
            </button>
          )}
          <button
            className="control-btn restart-btn"
            onClick={handleRestart}
            title="Restart explanation"
          >
            🔄 Restart
          </button>
        </div>
      </div>

      {isPlaying && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${(currentTime / (animation.duration || 10)) * 100}%`
            }}
          />
        </div>
      )}

      {/* Show both avatar video and animated text side-by-side if video is available */}
      {avatarVideoUrl ? (
        <div className="explanation-split-view">
          {/* Left side: Avatar video */}
          <div className="avatar-video-container">
            <video
              src={avatarVideoUrl}
              className="avatar-video"
              autoPlay={isPlaying}
              muted
              loop={false}
            />
            <div className="video-label">👩‍🏫 AI Teacher</div>
          </div>

          {/* Right side: Animated text */}
          <div className="animation-container">
            <AnimatePresence mode="sync">
              {animation.steps.map((step, index) => {
                const isVisible = visibleSteps.has(index);
                return (
                  <motion.div
                    key={step.id}
                    className={`animation-step ${isVisible ? 'active' : 'inactive'}`}
                    variants={getAnimationVariants(step.animation)}
                    initial="hidden"
                    animate={isVisible ? "visible" : "hidden"}
                    transition={{
                      duration: 0.6,
                      ease: "easeOut"
                    }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkMath]}
                      rehypePlugins={[rehypeKatex]}
                    >
                      {step.content}
                    </ReactMarkdown>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </div>
      ) : (
        /* Fallback: Show only animated text if no video */
        <div className="animation-container">
          <AnimatePresence mode="sync">
            {animation.steps.map((step, index) => {
              const isVisible = visibleSteps.has(index);
              return (
                <motion.div
                  key={step.id}
                  className={`animation-step ${isVisible ? 'active' : 'inactive'}`}
                  variants={getAnimationVariants(step.animation)}
                  initial="hidden"
                  animate={isVisible ? "visible" : "hidden"}
                  transition={{
                    duration: 0.6,
                    ease: "easeOut"
                  }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {step.content}
                  </ReactMarkdown>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};
