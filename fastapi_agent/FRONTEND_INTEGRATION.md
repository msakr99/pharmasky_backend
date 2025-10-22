# FastAPI Agent Frontend Integration Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# For React
npm install axios

# For Vue
npm install axios

# For Angular
npm install @angular/common @angular/http
```

### 2. Copy Files
```bash
# Copy TypeScript interfaces
cp fastapi_agent/types.ts src/types/

# Copy React components
cp fastapi_agent/react-components.tsx src/components/

# Copy Vue components
cp fastapi_agent/vue-components.vue src/components/

# Copy styles
cp fastapi_agent/styles.css src/styles/
```

## 📱 React Integration

### 1. Basic Usage
```jsx
import React from 'react';
import { AIAgentComponent } from './react-components';
import './styles.css';

function App() {
  return (
    <div className="App">
      <h1>PharmasSky AI Agent</h1>
      <AIAgentComponent 
        userId={123} 
        baseUrl="http://localhost:8001"
        mode="chat"
      />
    </div>
  );
}

export default App;
```

### 2. Advanced Usage with Hooks
```jsx
import React, { useState, useEffect } from 'react';
import { useFastAPIAgent } from './types';

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [userId] = useState(123);
  
  const {
    chat,
    voice,
    process,
    checkAvailability,
    createOrder
  } = useFastAPIAgent('http://localhost:8001');

  const handleChat = async (message) => {
    try {
      const response = await chat({
        message,
        context: { user_id: userId }
      });
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.message
      }]);
    } catch (error) {
      console.error('Chat error:', error);
    }
  };

  return (
    <div>
      {/* Your chat UI */}
    </div>
  );
}
```

### 3. Custom Hook
```jsx
import { useState, useCallback } from 'react';
import { FastAPIAgentClient } from './types';

export const useAIAgent = (userId, baseUrl = 'http://localhost:8001') => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const client = new FastAPIAgentClient(baseUrl);

  const sendMessage = useCallback(async (message, sessionId = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await client.chat({
        message,
        session_id: sessionId,
        context: { user_id: userId }
      });
      
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [client, userId]);

  return {
    sendMessage,
    isLoading,
    error
  };
};
```

## 🖼️ Vue.js Integration

### 1. Basic Usage
```vue
<template>
  <div class="app">
    <h1>PharmasSky AI Agent</h1>
    <FastAPIAgent 
      :user-id="123"
      base-url="http://localhost:8001"
      initial-mode="chat"
      @voice-response="handleVoiceResponse"
      @smart-response="handleSmartResponse"
      @search-results="handleSearchResults"
      @order-created="handleOrderCreated"
    />
  </div>
</template>

<script>
import FastAPIAgent from './vue-components.vue';

export default {
  name: 'App',
  components: {
    FastAPIAgent
  },
  methods: {
    handleVoiceResponse(data) {
      console.log('Voice response:', data);
    },
    handleSmartResponse(data) {
      console.log('Smart response:', data);
    },
    handleSearchResults(results) {
      console.log('Search results:', results);
    },
    handleOrderCreated(order) {
      console.log('Order created:', order);
    }
  }
};
</script>

<style>
@import './styles.css';
</style>
```

### 2. Composition API
```vue
<template>
  <div class="ai-agent-page">
    <div class="mode-selector">
      <button 
        v-for="mode in modes" 
        :key="mode.value"
        :class="{ active: currentMode === mode.value }"
        @click="currentMode = mode.value"
      >
        {{ mode.label }}
      </button>
    </div>
    
    <component :is="currentComponent" :user-id="userId" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { FastAPIAgentClient } from './types';

const userId = ref(123);
const currentMode = ref('chat');

const modes = [
  { value: 'chat', label: 'محادثة' },
  { value: 'voice', label: 'صوت' },
  { value: 'smart', label: 'معالجة ذكية' },
  { value: 'search', label: 'بحث' },
  { value: 'order', label: 'طلب' }
];

const currentComponent = computed(() => {
  const components = {
    chat: 'ChatComponent',
    voice: 'VoiceComponent',
    smart: 'SmartProcessingComponent',
    search: 'MedicineSearchComponent',
    order: 'OrderCreationComponent'
  };
  return components[currentMode.value];
});
</script>
```

## 🅰️ Angular Integration

### 1. Service
```typescript
// ai-agent.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AIAgentService {
  private baseUrl = 'http://localhost:8001';

  constructor(private http: HttpClient) {}

  chat(message: string, userId: number, sessionId?: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/agent/chat`, {
      message,
      session_id: sessionId,
      context: { user_id: userId }
    });
  }

  voice(audioBase64: string, userId: number, sessionId?: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/agent/voice`, {
      audio_base64: audioBase64,
      session_id: sessionId,
      context: { user_id: userId }
    });
  }

  process(query: string, userId: number, sessionId?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/agent/process`, {
      query,
      session_id: sessionId,
      context: { user_id: userId }
    });
  }

  checkAvailability(medicineName: string, userId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/agent/check-availability`, {
      medicine_name: medicineName,
      user_id: userId
    });
  }

  createOrder(medicineName: string, quantity: number, userId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/agent/create-order`, {
      medicine_name: medicineName,
      quantity,
      user_id: userId
    });
  }
}
```

### 2. Component
```typescript
// ai-agent.component.ts
import { Component, OnInit } from '@angular/core';
import { AIAgentService } from './ai-agent.service';

@Component({
  selector: 'app-ai-agent',
  templateUrl: './ai-agent.component.html',
  styleUrls: ['./ai-agent.component.css']
})
export class AIAgentComponent implements OnInit {
  messages: any[] = [];
  inputMessage = '';
  isLoading = false;
  userId = 123;

  constructor(private aiAgentService: AIAgentService) {}

  ngOnInit(): void {}

  async sendMessage(): Promise<void> {
    if (!this.inputMessage.trim()) return;

    this.isLoading = true;
    const message = this.inputMessage;
    this.inputMessage = '';

    // Add user message
    this.messages.push({ role: 'user', content: message });

    try {
      const response = await this.aiAgentService.chat(message, this.userId).toPromise();
      
      this.messages.push({ 
        role: 'assistant', 
        content: response.message 
      });
    } catch (error) {
      console.error('Chat error:', error);
      this.messages.push({ 
        role: 'assistant', 
        content: 'عذراً، حدث خطأ في المعالجة.' 
      });
    } finally {
      this.isLoading = false;
    }
  }
}
```

### 3. Template
```html
<!-- ai-agent.component.html -->
<div class="chat-container">
  <div class="messages">
    <div 
      *ngFor="let message of messages" 
      [class]="'message ' + message.role"
    >
      <div class="message-content">
        {{ message.content }}
      </div>
    </div>
    <div *ngIf="isLoading" class="message assistant">
      <div class="message-content">
        <div class="typing-indicator">...</div>
      </div>
    </div>
  </div>
  
  <form (ngSubmit)="sendMessage()" class="message-form">
    <input
      [(ngModel)]="inputMessage"
      type="text"
      placeholder="اكتب رسالتك هنا..."
      [disabled]="isLoading"
      class="message-input"
    />
    <button type="submit" [disabled]="isLoading || !inputMessage.trim()">
      إرسال
    </button>
  </form>
</div>
```

## 🎨 Styling

### 1. Import CSS
```css
/* In your main CSS file */
@import './styles.css';

/* Or in your component */
<style scoped>
@import './styles.css';
</style>
```

### 2. Custom Styling
```css
/* Custom theme */
.ai-agent-component {
  --primary-color: #007bff;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
}

.message.user .message-content {
  background: var(--primary-color);
  color: white;
}

.voice-button {
  background: var(--primary-color);
  transition: all 0.3s ease;
}

.voice-button:hover {
  background: var(--success-color);
  transform: scale(1.05);
}
```

## 🔧 Configuration

### 1. Environment Variables
```javascript
// config.js
export const config = {
  AI_AGENT_URL: process.env.REACT_APP_AI_AGENT_URL || 'http://localhost:8001',
  USER_ID: process.env.REACT_APP_USER_ID || 123
};
```

### 2. API Configuration
```javascript
// api-config.js
export const apiConfig = {
  baseURL: 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
};
```

## 🧪 Testing

### 1. Unit Tests
```javascript
// ai-agent.test.js
import { FastAPIAgentClient } from './types';

describe('FastAPIAgentClient', () => {
  let client;

  beforeEach(() => {
    client = new FastAPIAgentClient('http://localhost:8001');
  });

  it('should send chat message', async () => {
    const mockResponse = {
      message: 'Hello!',
      session_id: 123
    };

    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });

    const result = await client.chat({
      message: 'Hello',
      context: { user_id: 123 }
    });

    expect(result).toEqual(mockResponse);
  });
});
```

### 2. Integration Tests
```javascript
// integration.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AIAgentComponent } from './react-components';

describe('AIAgentComponent', () => {
  it('should send message and receive response', async () => {
    render(<AIAgentComponent userId={123} />);
    
    const input = screen.getByPlaceholderText('اكتب رسالتك هنا...');
    const button = screen.getByText('إرسال');
    
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
    });
  });
});
```

## 🚀 Deployment

### 1. Build Configuration
```javascript
// webpack.config.js
module.exports = {
  // ... other config
  resolve: {
    alias: {
      '@ai-agent': path.resolve(__dirname, 'src/ai-agent')
    }
  }
};
```

### 2. Docker Configuration
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

## 📊 Monitoring

### 1. Error Tracking
```javascript
// error-tracking.js
export const trackError = (error, context) => {
  console.error('AI Agent Error:', error, context);
  
  // Send to monitoring service
  if (window.gtag) {
    window.gtag('event', 'ai_agent_error', {
      error_message: error.message,
      context: JSON.stringify(context)
    });
  }
};
```

### 2. Performance Monitoring
```javascript
// performance.js
export const trackPerformance = (action, duration) => {
  console.log(`AI Agent ${action}: ${duration}ms`);
  
  // Send to analytics
  if (window.gtag) {
    window.gtag('event', 'ai_agent_performance', {
      action,
      duration
    });
  }
};
```

## 🎯 Best Practices

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Loading States**: Show loading indicators during API calls
3. **User Feedback**: Provide clear feedback for user actions
4. **Accessibility**: Ensure keyboard navigation and screen reader support
5. **Performance**: Use debouncing for search inputs
6. **Security**: Validate user inputs before sending to API
7. **Testing**: Write comprehensive tests for all components
8. **Documentation**: Keep API documentation up to date

## 🔗 Useful Links

- [FastAPI Agent API Documentation](./API_ENDPOINTS.md)
- [TypeScript Interfaces](./types.ts)
- [React Components](./react-components.tsx)
- [Vue Components](./vue-components.vue)
- [CSS Styles](./styles.css)

---

**Happy Coding! 🚀**
