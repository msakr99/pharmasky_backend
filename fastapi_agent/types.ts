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
