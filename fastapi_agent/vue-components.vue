<template>
  <!-- Chat Component -->
  <div class="chat-component" v-if="mode === 'chat'">
    <div class="messages" ref="messagesContainer">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        :class="['message', message.role]"
      >
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
      <div v-if="isLoading" class="message assistant">
        <div class="message-content">
          <div class="typing-indicator">...</div>
        </div>
      </div>
    </div>
    
    <form @submit.prevent="sendMessage" class="message-form">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="اكتب رسالتك هنا..."
        :disabled="isLoading"
        class="message-input"
      />
      <button type="submit" :disabled="isLoading || !inputMessage.trim()">
        إرسال
      </button>
    </form>
  </div>

  <!-- Voice Component -->
  <div class="voice-component" v-else-if="mode === 'voice'">
    <button
      @mousedown="startRecording"
      @mouseup="stopRecording"
      @touchstart="startRecording"
      @touchend="stopRecording"
      :disabled="isProcessing"
      :class="['voice-button', { recording: isRecording }]"
    >
      {{ isProcessing ? 'معالجة...' : isRecording ? 'تحدث الآن' : 'اضغط للتحدث' }}
    </button>
  </div>

  <!-- Smart Processing Component -->
  <div class="smart-processing" v-else-if="mode === 'smart'">
    <form @submit.prevent="processQuery" class="query-form">
      <input
        v-model="query"
        type="text"
        placeholder="اكتب طلبك هنا (مثال: عايز 10 علب باراسيتامول)..."
        :disabled="isProcessing"
        class="query-input"
      />
      <button type="submit" :disabled="isProcessing || !query.trim()">
        {{ isProcessing ? 'معالجة...' : 'معالجة ذكية' }}
      </button>
    </form>
  </div>

  <!-- Medicine Search Component -->
  <div class="medicine-search" v-else-if="mode === 'search'">
    <form @submit.prevent="searchMedicine" class="search-form">
      <input
        v-model="medicineName"
        type="text"
        placeholder="ابحث عن دواء..."
        :disabled="isSearching"
        class="search-input"
      />
      <button type="submit" :disabled="isSearching || !medicineName.trim()">
        {{ isSearching ? 'بحث...' : 'بحث' }}
      </button>
    </form>
    
    <div v-if="searchResults" class="search-results">
      <h3>نتائج البحث:</h3>
      <div v-if="searchResults.available" class="available-medicines">
        <div 
          v-for="(offer, index) in searchResults.offers" 
          :key="index" 
          class="medicine-card"
        >
          <h4>{{ offer.name }}</h4>
          <p>السعر الأصلي: {{ offer.original_price }} جنيه</p>
          <p>الخصم: {{ offer.discount_percentage }}%</p>
          <p>متوفر: {{ offer.available ? 'نعم' : 'لا' }}</p>
        </div>
      </div>
      <p v-else class="no-results">{{ searchResults.message }}</p>
    </div>
  </div>

  <!-- Order Creation Component -->
  <div class="order-creation" v-else-if="mode === 'order'">
    <form @submit.prevent="createOrder" class="order-form">
      <input
        v-model="orderMedicineName"
        type="text"
        placeholder="اسم الدواء"
        :disabled="isCreating"
        class="medicine-input"
      />
      <input
        v-model.number="orderQuantity"
        type="number"
        min="1"
        :disabled="isCreating"
        class="quantity-input"
      />
      <button type="submit" :disabled="isCreating || !orderMedicineName.trim()">
        {{ isCreating ? 'إنشاء...' : 'إنشاء طلب' }}
      </button>
    </form>
  </div>

  <!-- Mode Selector -->
  <div class="mode-selector">
    <button 
      v-for="modeOption in modes" 
      :key="modeOption.value"
      :class="{ active: mode === modeOption.value }"
      @click="setMode(modeOption.value)"
    >
      {{ modeOption.label }}
    </button>
  </div>
</template>

<script>
import { FastAPIAgentClient, blobToBase64, base64ToBlob } from './types';

export default {
  name: 'FastAPIAgent',
  props: {
    userId: {
      type: Number,
      required: true
    },
    baseUrl: {
      type: String,
      default: 'http://localhost:8001'
    },
    initialMode: {
      type: String,
      default: 'chat'
    }
  },
  data() {
    return {
      mode: this.initialMode,
      modes: [
        { value: 'chat', label: 'محادثة' },
        { value: 'voice', label: 'صوت' },
        { value: 'smart', label: 'معالجة ذكية' },
        { value: 'search', label: 'بحث' },
        { value: 'order', label: 'طلب' }
      ],
      
      // Chat data
      messages: [],
      inputMessage: '',
      isLoading: false,
      sessionId: null,
      
      // Voice data
      isRecording: false,
      isProcessing: false,
      mediaRecorder: null,
      audioChunks: [],
      
      // Smart processing data
      query: '',
      
      // Search data
      medicineName: '',
      isSearching: false,
      searchResults: null,
      
      // Order data
      orderMedicineName: '',
      orderQuantity: 1,
      isCreating: false,
      
      // Client
      client: null
    };
  },
  created() {
    this.client = new FastAPIAgentClient(this.baseUrl);
  },
  methods: {
    setMode(mode) {
      this.mode = mode;
    },
    
    // Chat methods
    async sendMessage() {
      if (!this.inputMessage.trim()) return;
      
      this.isLoading = true;
      const userMessage = this.inputMessage;
      this.inputMessage = '';
      
      // Add user message
      this.messages.push({ role: 'user', content: userMessage });
      
      try {
        const response = await this.client.chat({
          message: userMessage,
          session_id: this.sessionId,
          context: { user_id: this.userId }
        });
        
        this.messages.push({ role: 'assistant', content: response.message });
        this.sessionId = response.session_id;
      } catch (error) {
        console.error('Chat error:', error);
        this.messages.push({ 
          role: 'assistant', 
          content: 'عذراً، حدث خطأ في المعالجة. حاول مرة أخرى.' 
        });
      } finally {
        this.isLoading = false;
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    // Voice methods
    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };
        
        this.mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
          await this.processVoiceMessage(audioBlob);
          stream.getTracks().forEach(track => track.stop());
        };
        
        this.mediaRecorder.start();
        this.isRecording = true;
      } catch (error) {
        console.error('Error starting recording:', error);
      }
    },
    
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;
      }
    },
    
    async processVoiceMessage(audioBlob) {
      this.isProcessing = true;
      
      try {
        const base64Audio = await blobToBase64(audioBlob);
        
        const response = await this.client.voice({
          audio_base64: base64Audio,
          session_id: this.sessionId,
          context: { user_id: this.userId }
        });
        
        this.sessionId = response.session_id;
        
        // Play response audio
        const responseBlob = base64ToBlob(response.audio_base64);
        const audioUrl = URL.createObjectURL(responseBlob);
        const audio = new Audio(audioUrl);
        await audio.play();
        
        this.$emit('voice-response', {
          text: response.text,
          transcription: response.transcription
        });
      } catch (error) {
        console.error('Voice processing error:', error);
      } finally {
        this.isProcessing = false;
      }
    },
    
    // Smart processing methods
    async processQuery() {
      if (!this.query.trim()) return;
      
      this.isProcessing = true;
      const query = this.query;
      this.query = '';
      
      try {
        const response = await this.client.process({
          query,
          session_id: this.sessionId,
          context: { user_id: this.userId }
        });
        
        this.sessionId = response.session_id;
        this.$emit('smart-response', {
          response: response.response,
          actions: response.actions
        });
      } catch (error) {
        console.error('Processing error:', error);
      } finally {
        this.isProcessing = false;
      }
    },
    
    // Search methods
    async searchMedicine() {
      if (!this.medicineName.trim()) return;
      
      this.isSearching = true;
      
      try {
        const response = await this.client.checkAvailability({
          medicine_name: this.medicineName,
          user_id: this.userId
        });
        
        this.searchResults = response;
        this.$emit('search-results', response);
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        this.isSearching = false;
      }
    },
    
    // Order methods
    async createOrder() {
      if (!this.orderMedicineName.trim() || this.orderQuantity <= 0) return;
      
      this.isCreating = true;
      
      try {
        const response = await this.client.createOrder({
          medicine_name: this.orderMedicineName,
          quantity: this.orderQuantity,
          user_id: this.userId
        });
        
        this.$emit('order-created', response);
        
        // Reset form
        this.orderMedicineName = '';
        this.orderQuantity = 1;
      } catch (error) {
        console.error('Order creation error:', error);
      } finally {
        this.isCreating = false;
      }
    }
  }
};
</script>

<style scoped>
/* Import the main styles */
@import './styles.css';

/* Component-specific styles */
.mode-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.mode-selector button {
  padding: 10px 20px;
  border: 2px solid #007bff;
  background: white;
  color: #007bff;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.mode-selector button:hover {
  background: #007bff;
  color: white;
}

.mode-selector button.active {
  background: #007bff;
  color: white;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .mode-selector {
    flex-direction: column;
  }
  
  .mode-selector button {
    width: 100%;
  }
}
</style>
