export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  imageData?: string; // Base64 image data for display in chat
  explanationAnimation?: AnimationData; // Animation steps for explanation
  explanationAudio?: string; // Base64 encoded audio
  explanationDuration?: number; // Duration in seconds
  avatarVideoUrl?: string; // HeyGen avatar video URL
  avatarVideoId?: string; // HeyGen video ID
}

export interface AnimationData {
  narration: string;
  steps: AnimationStep[];
  duration?: number;
}

export interface AnimationStep {
  id: string;
  content: string;
  startTime: number; // Seconds
  duration: number; // Seconds
  animation: 'fadeIn' | 'slideIn' | 'highlight' | 'scale' | 'pulse';
}

export interface Source {
  content: string;
  metadata: {
    source: string;
    page?: number;
  };
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  use_rag?: boolean;
  image_data?: string; // Base64 encoded image
  extracted_text?: string; // OCR extracted text from image
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources?: Source[];
}

export interface UploadResponse {
  status: string;
  message: string;
  details?: {
    files_processed: number;
    total_chunks: number;
    filenames: string[];
  };
}
