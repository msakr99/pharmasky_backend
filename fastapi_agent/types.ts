// FastAPI Agent TypeScript Interfaces

export interface ChatRequest {
  message: string;
  session_id?: number;
  context?: {
    user_id?: number;
    [key: string]: any;
  };
}

export interface ChatResponse {
  message: string;
  session_id: number;
}

export interface VoiceRequest {
  audio_base64: string;
  session_id?: number;
  context?: {
    user_id?: number;
    [key: string]: any;
  };
}

export interface VoiceResponse {
  text: string;
  audio_base64: string;
  session_id: number;
  transcription: string;
}

export interface CallRequest {
  audio_chunk_base64: string;
  session_id?: number;
  context?: {
    user_id?: number;
    [key: string]: any;
  };
}

export interface CallResponse {
  audio_response_base64: string;
  text_response: string;
  is_final: boolean;
}

export interface ProcessRequest {
  query: string;
  session_id?: string;
  context?: {
    user_id?: number;
    [key: string]: any;
  };
}

export interface ProcessResponse {
  success: boolean;
  response: string;
  actions: Array<{
    action: string;
    result: any;
  }>;
  session_id?: string;
  metadata?: {
    intent?: string;
    entities?: Record<string, any>;
    [key: string]: any;
  };
}

// Function APIs
export interface CheckAvailabilityRequest {
  medicine_name: string;
  user_id?: number;
}

export interface CheckAvailabilityResponse {
  success: boolean;
  available: boolean;
  message: string;
  offers: Array<{
    name: string;
    available: boolean;
    original_price: number;
    discount_percentage: number;
  }>;
}

export interface SuggestAlternativeRequest {
  medicine_name: string;
}

export interface SuggestAlternativeResponse {
  success: boolean;
  found: boolean;
  message: string;
  original_product?: string;
  alternatives: Array<{
    id: number;
    name: string;
    english_name: string;
    price: number;
    company: string;
    effective_material: string;
  }>;
}

export interface CreateOrderRequest {
  medicine_name: string;
  quantity: number;
  user_id: number;
}

export interface CreateOrderResponse {
  success: boolean;
  message: string;
  order_id?: number;
  product?: string;
  quantity?: number;
  unit_price?: number;
  total_price?: number;
  discount_percentage?: number;
  amount_saved?: number;
}

export interface TrackOrderRequest {
  order_id: number;
  user_id: number;
}

export interface TrackOrderResponse {
  success: boolean;
  found: boolean;
  message: string;
  order?: {
    order_id: number;
    status: string;
    total_price: number;
    items_count: number;
    created_at: string;
    items: Array<{
      product: string;
      quantity: number;
      price: number;
      status: string;
    }>;
  };
}

export interface CancelOrderRequest {
  order_id: number;
  user_id: number;
}

export interface CancelOrderResponse {
  success: boolean;
  message: string;
}

export interface SubmitComplaintRequest {
  subject: string;
  body: string;
  user_id: number;
}

export interface SubmitComplaintResponse {
  success: boolean;
  message: string;
  complaint_id?: number;
  subject?: string;
  created_at?: string;
}

export interface GetWishlistResponse {
  success: boolean;
  message: string;
  wishlist: Array<{
    product_id: number;
    name: string;
    english_name: string;
    price: number;
    company: string;
    effective_material: string;
    shape: string;
    in_max_offer: boolean;
    added_at: string;
  }>;
  count: number;
}

export interface AddToWishlistRequest {
  product_name: string;
  user_id: number;
}

export interface AddToWishlistResponse {
  success: boolean;
  message: string;
  product?: {
    id: number;
    name: string;
    english_name: string;
    price: number;
    company: string;
    effective_material: string;
  };
  already_added?: boolean;
}

export interface GetOrderTotalResponse {
  success: boolean;
  message: string;
  grand_total: number;
  total_items: number;
  orders_count: number;
  orders: Array<{
    order_id: number;
    items: Array<{
      product: string;
      quantity: number;
      unit_price: number;
      total: number;
    }>;
    total: number;
    status: string;
  }>;
  summary: string[];
}

// API Client Class
export class FastAPIAgentClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'POST',
    data?: any
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Chat APIs
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/agent/chat', 'POST', request);
  }

  async voice(request: VoiceRequest): Promise<VoiceResponse> {
    return this.request<VoiceResponse>('/agent/voice', 'POST', request);
  }

  async call(request: CallRequest): Promise<CallResponse> {
    return this.request<CallResponse>('/agent/call', 'POST', request);
  }

  async process(request: ProcessRequest): Promise<ProcessResponse> {
    return this.request<ProcessResponse>('/agent/process', 'POST', request);
  }

  // Function APIs
  async checkAvailability(request: CheckAvailabilityRequest): Promise<CheckAvailabilityResponse> {
    return this.request<CheckAvailabilityResponse>('/agent/check-availability', 'POST', request);
  }

  async suggestAlternative(request: SuggestAlternativeRequest): Promise<SuggestAlternativeResponse> {
    return this.request<SuggestAlternativeResponse>('/agent/suggest-alternative', 'POST', request);
  }

  async createOrder(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    return this.request<CreateOrderResponse>('/agent/create-order', 'POST', request);
  }

  async trackOrder(request: TrackOrderRequest): Promise<TrackOrderResponse> {
    return this.request<TrackOrderResponse>('/agent/track-order', 'POST', request);
  }

  async cancelOrder(request: CancelOrderRequest): Promise<CancelOrderResponse> {
    return this.request<CancelOrderResponse>('/agent/cancel-order', 'POST', request);
  }

  async submitComplaint(request: SubmitComplaintRequest): Promise<SubmitComplaintResponse> {
    return this.request<SubmitComplaintResponse>('/agent/submit-complaint', 'POST', request);
  }

  async getWishlist(userId: number): Promise<GetWishlistResponse> {
    return this.request<GetWishlistResponse>(`/agent/get-wishlist/${userId}`, 'GET');
  }

  async addToWishlist(request: AddToWishlistRequest): Promise<AddToWishlistResponse> {
    return this.request<AddToWishlistResponse>('/agent/add-to-wishlist', 'POST', request);
  }

  async getOrderTotal(userId: number): Promise<GetOrderTotalResponse> {
    return this.request<GetOrderTotalResponse>(`/agent/get-order-total/${userId}`, 'GET');
  }
}

// Utility functions
export const blobToBase64 = (blob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result as string;
      resolve(result.split(',')[1]);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

export const base64ToBlob = (base64: string, mimeType: string = 'audio/wav'): Blob => {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
};

// React Hook Example
export const useFastAPIAgent = (baseUrl?: string) => {
  const client = new FastAPIAgentClient(baseUrl);

  return {
    chat: client.chat.bind(client),
    voice: client.voice.bind(client),
    call: client.call.bind(client),
    process: client.process.bind(client),
    checkAvailability: client.checkAvailability.bind(client),
    suggestAlternative: client.suggestAlternative.bind(client),
    createOrder: client.createOrder.bind(client),
    trackOrder: client.trackOrder.bind(client),
    cancelOrder: client.cancelOrder.bind(client),
    submitComplaint: client.submitComplaint.bind(client),
    getWishlist: client.getWishlist.bind(client),
    addToWishlist: client.addToWishlist.bind(client),
    getOrderTotal: client.getOrderTotal.bind(client),
  };
};
