# FastAPI Agent API Endpoints

## 🚀 Base URL
```
http://localhost:8001
```

## 📡 API Endpoints

### 1. Chat API
```http
POST /agent/chat
Content-Type: application/json

{
  "message": "عايز باراسيتامول",
  "session_id": 123,
  "context": {
    "user_id": 456
  }
}
```

**Response:**
```json
{
  "message": "أهلاً! باراسيتامول سعره 15 جنيه، عليه خصم 17%! 🎉 حضرتك عايز كام علبة؟",
  "session_id": 123
}
```

### 2. Voice API
```http
POST /agent/voice
Content-Type: application/json

{
  "audio_base64": "base64_encoded_audio_data",
  "session_id": 123,
  "context": {
    "user_id": 456
  }
}
```

**Response:**
```json
{
  "text": "أهلاً! باراسيتامول سعره 15 جنيه، عليه خصم 17%!",
  "audio_base64": "base64_encoded_response_audio",
  "session_id": 123,
  "transcription": "عايز باراسيتامول"
}
```

### 3. Call API (Real-time)
```http
POST /agent/call
Content-Type: application/json

{
  "audio_chunk_base64": "base64_encoded_audio_chunk",
  "session_id": 123,
  "context": {
    "user_id": 456
  }
}
```

**Response:**
```json
{
  "audio_response_base64": "base64_encoded_response_audio",
  "text_response": "أهلاً! باراسيتامول سعره 15 جنيه، عليه خصم 17%!",
  "is_final": true
}
```

### 4. Process API (Smart Processing)
```http
POST /agent/process
Content-Type: application/json

{
  "query": "عايز 10 علب باراسيتامول",
  "session_id": "session_123",
  "context": {
    "user_id": 456
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "تمام! ضفت 10 علب باراسيتامول ✅ في حاجة تانية؟",
  "actions": [
    {
      "action": "create_order",
      "result": {
        "success": true,
        "order_id": 789,
        "message": "تم إنشاء الطلب بنجاح"
      }
    }
  ],
  "session_id": "session_123",
  "metadata": {
    "intent": "order",
    "entities": {
      "product": "باراسيتامول",
      "quantity": 10
    }
  }
}
```

## 🛠️ Function APIs

### 5. Check Availability
```http
POST /agent/check-availability
Content-Type: application/json

{
  "medicine_name": "باراسيتامول",
  "user_id": 456
}
```

### 6. Suggest Alternative
```http
POST /agent/suggest-alternative
Content-Type: application/json

{
  "medicine_name": "باراسيتامول"
}
```

### 7. Create Order
```http
POST /agent/create-order
Content-Type: application/json

{
  "medicine_name": "باراسيتامول",
  "quantity": 10,
  "user_id": 456
}
```

### 8. Track Order
```http
POST /agent/track-order
Content-Type: application/json

{
  "order_id": 789,
  "user_id": 456
}
```

### 9. Cancel Order
```http
POST /agent/cancel-order
Content-Type: application/json

{
  "order_id": 789,
  "user_id": 456
}
```

### 10. Submit Complaint
```http
POST /agent/submit-complaint
Content-Type: application/json

{
  "subject": "مشكلة في التوصيل",
  "body": "الطلب وصل متأخر",
  "user_id": 456
}
```

### 11. Get Wishlist
```http
GET /agent/get-wishlist/456
```

### 12. Add to Wishlist
```http
POST /agent/add-to-wishlist
Content-Type: application/json

{
  "product_name": "فيتامين د",
  "user_id": 456
}
```

### 13. Get Order Total
```http
GET /agent/get-order-total/456
```

## 🔧 JavaScript Examples

### Basic Fetch Examples
```javascript
// Chat API
const sendMessage = async (message, userId, sessionId = null) => {
  const response = await fetch('http://localhost:8001/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
      context: { user_id: userId }
    })
  });
  return response.json();
};

// Voice API
const sendVoiceMessage = async (audioBase64, userId, sessionId = null) => {
  const response = await fetch('http://localhost:8001/agent/voice', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio_base64: audioBase64,
      session_id: sessionId,
      context: { user_id: userId }
    })
  });
  return response.json();
};

// Function APIs
const checkAvailability = async (medicineName, userId) => {
  const response = await fetch('http://localhost:8001/agent/check-availability', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      medicine_name: medicineName,
      user_id: userId
    })
  });
  return response.json();
};
```

### Axios Examples
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: { 'Content-Type': 'application/json' }
});

// Chat
const chat = (message, userId, sessionId) => 
  api.post('/agent/chat', {
    message,
    session_id: sessionId,
    context: { user_id: userId }
  });

// Voice
const voice = (audioBase64, userId, sessionId) =>
  api.post('/agent/voice', {
    audio_base64: audioBase64,
    session_id: sessionId,
    context: { user_id: userId }
  });

// Functions
const checkAvailability = (medicineName, userId) =>
  api.post('/agent/check-availability', {
    medicine_name: medicineName,
    user_id: userId
  });
```

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Response text",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

## 🚀 Quick Start

1. **Start FastAPI Agent:**
   ```bash
   cd fastapi_agent
   python main.py
   ```

2. **Test API:**
   ```bash
   curl -X POST http://localhost:8001/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "مرحبا", "context": {"user_id": 123}}'
   ```
