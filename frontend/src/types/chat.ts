export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
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
