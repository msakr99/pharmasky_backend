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

## 🔧 JavaScript/React Examples

### Chat Component
```javascript
const sendMessage = async (message, userId, sessionId = null) => {
  try {
    const response = await fetch('http://localhost:8001/agent/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId,
        context: { user_id: userId }
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Chat error:', error);
    throw error;
  }
};
```

### Voice Component
```javascript
const sendVoiceMessage = async (audioBlob, userId, sessionId = null) => {
  try {
    // Convert audio to base64
    const base64Audio = await blobToBase64(audioBlob);
    
    const response = await fetch('http://localhost:8001/agent/voice', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        audio_base64: base64Audio,
        session_id: sessionId,
        context: { user_id: userId }
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Voice error:', error);
    throw error;
  }
};

const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};
```

### Function Calling
```javascript
const checkAvailability = async (medicineName, userId) => {
  try {
    const response = await fetch('http://localhost:8001/agent/check-availability', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        medicine_name: medicineName,
        user_id: userId
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Check availability error:', error);
    throw error;
  }
};

const createOrder = async (medicineName, quantity, userId) => {
  try {
    const response = await fetch('http://localhost:8001/agent/create-order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        medicine_name: medicineName,
        quantity: quantity,
        user_id: userId
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Create order error:', error);
    throw error;
  }
};
```

## 🎯 Usage Examples

### 1. Simple Chat
```javascript
// Send text message
const result = await sendMessage("عايز باراسيتامول", 123, 456);
console.log(result.message); // AI response
console.log(result.session_id); // Session ID
```

### 2. Voice Interaction
```javascript
// Send voice message
const result = await sendVoiceMessage(audioBlob, 123, 456);
console.log(result.text); // Transcribed text
console.log(result.audio_base64); // AI response audio
```

### 3. Smart Processing
```javascript
// Smart processing with function calling
const result = await fetch('http://localhost:8001/agent/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "عايز 10 علب باراسيتامول",
    context: { user_id: 123 }
  })
});

const data = await result.json();
console.log(data.response); // AI response
console.log(data.actions); // Executed actions
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

## 🔐 Authentication

Currently, the API uses user_id in the context. For production, consider implementing proper authentication headers:

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer your-jwt-token'
};
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

3. **Integrate with Frontend:**
   ```javascript
   // Use the examples above in your React/Vue/Angular app
   ```
