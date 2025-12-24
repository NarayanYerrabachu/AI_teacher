import React, { useState, useRef } from 'react';
import Tesseract from 'tesseract.js';
import './ChatInput.css';

interface ChatInputProps {
  onSendMessage: (message: string, imageData?: string, extractedText?: string) => void;
  onUploadFiles: (files: File[]) => void;
  disabled?: boolean;
}

interface ImagePreview {
  file: File;
  dataUrl: string;
  extractedText: string;
  isProcessing: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onUploadFiles,
  disabled = false
}) => {
  const [message, setMessage] = useState('');
  const [imagePreview, setImagePreview] = useState<ImagePreview | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Allow submit if there's either a message or an image
    if ((message.trim() || imagePreview) && !disabled) {
      const imageData = imagePreview?.dataUrl;
      const extractedText = imagePreview?.extractedText;
      // If no message but has image, use extracted text as message
      const finalMessage = message.trim() || extractedText || 'Analyze this image';
      onSendMessage(finalMessage, imageData, extractedText);
      setMessage('');
      setImagePreview(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onUploadFiles(files);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const processImage = async (file: File) => {
    // Create data URL for preview
    const reader = new FileReader();
    reader.onload = async (e) => {
      const dataUrl = e.target?.result as string;

      // Set initial preview with loading state
      setImagePreview({
        file,
        dataUrl,
        extractedText: '',
        isProcessing: true
      });

      try {
        // Perform OCR
        const result = await Tesseract.recognize(
          dataUrl,
          'eng',
          {
            logger: (m) => {
              if (m.status === 'recognizing text') {
                console.log(`OCR Progress: ${(m.progress * 100).toFixed(0)}%`);
              }
            }
          }
        );

        const extractedText = result.data.text.trim();

        // Update preview with extracted text (but don't add to message input)
        setImagePreview({
          file,
          dataUrl,
          extractedText,
          isProcessing: false
        });
      } catch (error) {
        console.error('OCR Error:', error);
        setImagePreview({
          file,
          dataUrl,
          extractedText: 'Error extracting text from image',
          isProcessing: false
        });
      }
    };
    reader.readAsDataURL(file);
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      processImage(file);
      // Reset input
      if (imageInputRef.current) {
        imageInputRef.current.value = '';
      }
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.startsWith('image/')) {
        e.preventDefault();
        const file = item.getAsFile();
        if (file) {
          processImage(file);
        }
        break;
      }
    }
  };

  const handleRemoveImage = () => {
    setImagePreview(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      {imagePreview && (
        <div className="image-preview-container">
          <div className="image-preview-header">
            <span>Image Preview</span>
            <button
              type="button"
              className="remove-image-btn"
              onClick={handleRemoveImage}
              title="Remove image"
            >
              ✕
            </button>
          </div>
          <div className="image-preview-content">
            <img src={imagePreview.dataUrl} alt="Preview" className="preview-image" />
            <div className="extracted-text-preview">
              {imagePreview.isProcessing ? (
                <div className="ocr-loading">
                  <div className="spinner"></div>
                  <span>Extracting text...</span>
                </div>
              ) : (
                <>
                  <div className="extracted-text-header">Extracted Text:</div>
                  <div className="extracted-text-content">
                    {imagePreview.extractedText || 'No text found'}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="input-wrapper">
        <button
          type="button"
          className="upload-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          title="Upload PDF files"
        >
          📎
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />

        <button
          type="button"
          className="image-upload-button"
          onClick={() => imageInputRef.current?.click()}
          disabled={disabled || imagePreview !== null}
          title="Upload image for OCR"
        >
          🖼️
        </button>
        <input
          ref={imageInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          style={{ display: 'none' }}
        />

        <textarea
          ref={textareaRef}
          className="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder="Type your message or paste an image... (Shift+Enter for new line)"
          disabled={disabled}
          rows={1}
        />
        {disabled && (
          <div className="loading-indicator">
            <div className="spinner"></div>
          </div>
        )}
        <button
          type="submit"
          className="send-button"
          disabled={(!message.trim() && !imagePreview) || disabled}
        >
          ➤
        </button>
      </div>
    </form>
  );
};
