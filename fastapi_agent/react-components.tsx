import React, { useState, useRef, useCallback } from 'react';
import { 
  FastAPIAgentClient, 
  ChatRequest, 
  ChatResponse, 
  VoiceRequest, 
  VoiceResponse,
  ProcessRequest,
  ProcessResponse,
  CheckAvailabilityRequest,
  CheckAvailabilityResponse,
  CreateOrderRequest,
  CreateOrderResponse,
  blobToBase64,
  base64ToBlob
} from './types';

// Chat Component
interface ChatComponentProps {
  userId: number;
  baseUrl?: string;
  onMessage?: (message: string) => void;
}

export const ChatComponent: React.FC<ChatComponentProps> = ({ 
  userId, 
  baseUrl = 'http://localhost:8001',
  onMessage 
}) => {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  
  const client = new FastAPIAgentClient(baseUrl);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setIsLoading(true);
    
    // Add user message
    const newMessages = [...messages, { role: 'user' as const, content: message }];
    setMessages(newMessages);

    try {
      const request: ChatRequest = {
        message,
        session_id: sessionId || undefined,
        context: { user_id: userId }
      };

      const response: ChatResponse = await client.chat(request);
      
      // Add assistant response
      setMessages([...newMessages, { role: 'assistant', content: response.message }]);
      setSessionId(response.session_id);
      
      if (onMessage) {
        onMessage(response.message);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: 'عذراً، حدث خطأ في المعالجة. حاول مرة أخرى.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, sessionId, userId, client, onMessage]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputMessage);
    setInputMessage('');
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">...</div>
            </div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="اكتب رسالتك هنا..."
          disabled={isLoading}
          className="message-input"
        />
        <button type="submit" disabled={isLoading || !inputMessage.trim()}>
          إرسال
        </button>
      </form>
    </div>
  );
};

// Voice Component
interface VoiceComponentProps {
  userId: number;
  baseUrl?: string;
  onTranscription?: (text: string) => void;
  onResponse?: (response: string) => void;
}

export const VoiceComponent: React.FC<VoiceComponentProps> = ({ 
  userId, 
  baseUrl = 'http://localhost:8001',
  onTranscription,
  onResponse
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  
  const client = new FastAPIAgentClient(baseUrl);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const processVoiceMessage = useCallback(async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    try {
      const base64Audio = await blobToBase64(audioBlob);
      
      const request: VoiceRequest = {
        audio_base64: base64Audio,
        session_id: sessionId || undefined,
        context: { user_id: userId }
      };

      const response: VoiceResponse = await client.voice(request);
      
      setSessionId(response.session_id);
      
      if (onTranscription) {
        onTranscription(response.transcription);
      }
      
      if (onResponse) {
        onResponse(response.text);
      }

      // Play response audio
      const responseBlob = base64ToBlob(response.audio_base64);
      const audioUrl = URL.createObjectURL(responseBlob);
      const audio = new Audio(audioUrl);
      await audio.play();
      
    } catch (error) {
      console.error('Voice processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [sessionId, userId, client, onTranscription, onResponse]);

  return (
    <div className="voice-component">
      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        disabled={isProcessing}
        className={`voice-button ${isRecording ? 'recording' : ''}`}
      >
        {isProcessing ? 'معالجة...' : isRecording ? 'تحدث الآن' : 'اضغط للتحدث'}
      </button>
    </div>
  );
};

// Smart Processing Component
interface SmartProcessingComponentProps {
  userId: number;
  baseUrl?: string;
  onResponse?: (response: string, actions: any[]) => void;
}

export const SmartProcessingComponent: React.FC<SmartProcessingComponentProps> = ({ 
  userId, 
  baseUrl = 'http://localhost:8001',
  onResponse
}) => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const client = new FastAPIAgentClient(baseUrl);

  const processQuery = useCallback(async (text: string) => {
    if (!text.trim()) return;

    setIsProcessing(true);
    
    try {
      const request: ProcessRequest = {
        query: text,
        session_id: sessionId || undefined,
        context: { user_id: userId }
      };

      const response: ProcessResponse = await client.process(request);
      
      setSessionId(response.session_id || null);
      
      if (onResponse) {
        onResponse(response.response, response.actions);
      }
    } catch (error) {
      console.error('Processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [sessionId, userId, client, onResponse]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    processQuery(query);
    setQuery('');
  };

  return (
    <div className="smart-processing">
      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="اكتب طلبك هنا (مثال: عايز 10 علب باراسيتامول)..."
          disabled={isProcessing}
          className="query-input"
        />
        <button type="submit" disabled={isProcessing || !query.trim()}>
          {isProcessing ? 'معالجة...' : 'معالجة ذكية'}
        </button>
      </form>
    </div>
  );
};

// Medicine Search Component
interface MedicineSearchComponentProps {
  userId: number;
  baseUrl?: string;
  onResults?: (results: CheckAvailabilityResponse) => void;
}

export const MedicineSearchComponent: React.FC<MedicineSearchComponentProps> = ({ 
  userId, 
  baseUrl = 'http://localhost:8001',
  onResults
}) => {
  const [medicineName, setMedicineName] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<CheckAvailabilityResponse | null>(null);
  
  const client = new FastAPIAgentClient(baseUrl);

  const searchMedicine = useCallback(async (name: string) => {
    if (!name.trim()) return;

    setIsSearching(true);
    
    try {
      const request: CheckAvailabilityRequest = {
        medicine_name: name,
        user_id: userId
      };

      const response: CheckAvailabilityResponse = await client.checkAvailability(request);
      setResults(response);
      
      if (onResults) {
        onResults(response);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  }, [userId, client, onResults]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    searchMedicine(medicineName);
  };

  return (
    <div className="medicine-search">
      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          value={medicineName}
          onChange={(e) => setMedicineName(e.target.value)}
          placeholder="ابحث عن دواء..."
          disabled={isSearching}
          className="search-input"
        />
        <button type="submit" disabled={isSearching || !medicineName.trim()}>
          {isSearching ? 'بحث...' : 'بحث'}
        </button>
      </form>
      
      {results && (
        <div className="search-results">
          <h3>نتائج البحث:</h3>
          {results.available ? (
            <div className="available-medicines">
              {results.offers.map((offer, index) => (
                <div key={index} className="medicine-card">
                  <h4>{offer.name}</h4>
                  <p>السعر الأصلي: {offer.original_price} جنيه</p>
                  <p>الخصم: {offer.discount_percentage}%</p>
                  <p>متوفر: {offer.available ? 'نعم' : 'لا'}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-results">{results.message}</p>
          )}
        </div>
      )}
    </div>
  );
};

// Order Creation Component
interface OrderCreationComponentProps {
  userId: number;
  baseUrl?: string;
  onOrderCreated?: (order: CreateOrderResponse) => void;
}

export const OrderCreationComponent: React.FC<OrderCreationComponentProps> = ({ 
  userId, 
  baseUrl = 'http://localhost:8001',
  onOrderCreated
}) => {
  const [medicineName, setMedicineName] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [isCreating, setIsCreating] = useState(false);
  
  const client = new FastAPIAgentClient(baseUrl);

  const createOrder = useCallback(async (name: string, qty: number) => {
    if (!name.trim() || qty <= 0) return;

    setIsCreating(true);
    
    try {
      const request: CreateOrderRequest = {
        medicine_name: name,
        quantity: qty,
        user_id: userId
      };

      const response: CreateOrderResponse = await client.createOrder(request);
      
      if (onOrderCreated) {
        onOrderCreated(response);
      }
    } catch (error) {
      console.error('Order creation error:', error);
    } finally {
      setIsCreating(false);
    }
  }, [userId, client, onOrderCreated]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createOrder(medicineName, quantity);
  };

  return (
    <div className="order-creation">
      <form onSubmit={handleSubmit} className="order-form">
        <input
          type="text"
          value={medicineName}
          onChange={(e) => setMedicineName(e.target.value)}
          placeholder="اسم الدواء"
          disabled={isCreating}
          className="medicine-input"
        />
        <input
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
          min="1"
          disabled={isCreating}
          className="quantity-input"
        />
        <button type="submit" disabled={isCreating || !medicineName.trim()}>
          {isCreating ? 'إنشاء...' : 'إنشاء طلب'}
        </button>
      </form>
    </div>
  );
};

// Main AI Agent Component
interface AIAgentComponentProps {
  userId: number;
  baseUrl?: string;
  mode?: 'chat' | 'voice' | 'smart' | 'search' | 'order';
}

export const AIAgentComponent: React.FC<AIAgentComponentProps> = ({ 
  userId, 
  baseUrl = 'http://localhost:8001',
  mode = 'chat'
}) => {
  const [currentMode, setCurrentMode] = useState(mode);

  const renderComponent = () => {
    switch (currentMode) {
      case 'chat':
        return <ChatComponent userId={userId} baseUrl={baseUrl} />;
      case 'voice':
        return <VoiceComponent userId={userId} baseUrl={baseUrl} />;
      case 'smart':
        return <SmartProcessingComponent userId={userId} baseUrl={baseUrl} />;
      case 'search':
        return <MedicineSearchComponent userId={userId} baseUrl={baseUrl} />;
      case 'order':
        return <OrderCreationComponent userId={userId} baseUrl={baseUrl} />;
      default:
        return <ChatComponent userId={userId} baseUrl={baseUrl} />;
    }
  };

  return (
    <div className="ai-agent-component">
      <div className="mode-selector">
        <button 
          className={currentMode === 'chat' ? 'active' : ''}
          onClick={() => setCurrentMode('chat')}
        >
          محادثة
        </button>
        <button 
          className={currentMode === 'voice' ? 'active' : ''}
          onClick={() => setCurrentMode('voice')}
        >
          صوت
        </button>
        <button 
          className={currentMode === 'smart' ? 'active' : ''}
          onClick={() => setCurrentMode('smart')}
        >
          معالجة ذكية
        </button>
        <button 
          className={currentMode === 'search' ? 'active' : ''}
          onClick={() => setCurrentMode('search')}
        >
          بحث
        </button>
        <button 
          className={currentMode === 'order' ? 'active' : ''}
          onClick={() => setCurrentMode('order')}
        >
          طلب
        </button>
      </div>
      
      <div className="component-container">
        {renderComponent()}
      </div>
    </div>
  );
};
