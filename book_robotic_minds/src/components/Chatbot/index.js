import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

/**
 * Chatbot component for interacting with the RAG Agent API.
 * Allows users to ask questions about the book content and receive grounded responses.
 */
const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const messagesEndRef = useRef(null);

  // Toggle chat visibility
  const toggleChat = () => {
    setShowChat(!showChat);
  };

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get selected text from the page if available
      const selectedText = window.getSelection()?.toString()?.trim() || null;

      // Determine the API base URL based on environment
      const apiBaseUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? '' // For production deployment, use relative path to the same domain
        : 'http://localhost:8000'; // For local development

      // Call the backend API
      const response = await fetch(`${apiBaseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          selected_text: selectedText || undefined,
          top_k: 5,
          min_score: 0.3
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        text: data.answer,
        sender: 'bot',
        confidence: data.confidence_score,
        sources: data.sources_used,
        processingTime: data.processing_time,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        isError: true,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      {/* Chat launcher button */}
      {!showChat && (
        <button className="chatbot-launcher" onClick={toggleChat}>
          💬 Ask BookBot
        </button>
      )}

      {/* Chat interface */}
      {showChat && (
        <div className="chatbot-wrapper">
          <div className="chatbot-header">
            <h3>Book Assistant</h3>
            <button className="chatbot-close" onClick={toggleChat}>
              ×
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="chatbot-welcome">
                <p>Hello! I'm your Book Assistant. Ask me anything about the content in this book!</p>
                <p>You can also select text on the page and ask questions about it.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`chatbot-message ${
                    message.sender === 'user' ? 'user-message' : 'bot-message'
                  }`}
                >
                  <div className="message-content">
                    <p>{message.text}</p>

                    {message.sender === 'bot' && !message.isError && (
                      <>
                        {message.confidence !== undefined && (
                          <div className="message-meta">
                            <small>Confidence: {(message.confidence * 100).toFixed(1)}%</small>
                          </div>
                        )}

                        {message.sources && message.sources.length > 0 && (
                          <div className="message-sources">
                            <strong>Sources:</strong>
                            <ul>
                              {message.sources.slice(0, 3).map((source, idx) => (
                                <li key={idx}>
                                  <a href={source} target="_blank" rel="noopener noreferrer">
                                    {new URL(source).hostname}
                                  </a>
                                </li>
                              ))}
                              {message.sources.length > 3 && (
                                <li>+ {message.sources.length - 3} more sources</li>
                              )}
                            </ul>
                          </div>
                        )}
                      </>
                    )}

                    {message.isError && (
                      <div className="message-error">
                        <small>Error occurred while processing your request.</small>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {isLoading && (
              <div className="chatbot-message bot-message">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="chatbot-input-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question about this book..."
              disabled={isLoading}
              className="chatbot-input"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="chatbot-send-button"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Chatbot;