// lib/types.ts - TypeScript Types
export interface Call {
  id: number;
  session_id: string;
  pharmacy: {
    id: number;
    name: string;
  } | null;
  user: {
    id: number;
    username: string;
  } | null;
  status: 'active' | 'completed' | 'failed' | 'cancelled';
  duration: number;
  summary: string;
  created_at: string;
  ended_at: string | null;
  actions_count: number;
}

export interface CallDetail extends Call {
  metadata: Record<string, any>;
  audio_file: string | null;
  updated_at: string;
  transcripts: Transcript[];
  actions: Action[];
}

export interface Transcript {
  id: number;
  speaker: 'user' | 'assistant' | 'system';
  text: string;
  timestamp: number;
  created_at: string;
}

export interface Action {
  id: number;
  action_type: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
  status: 'pending' | 'success' | 'failed';
  error_message: string;
  created_at: string;
  completed_at: string | null;
}

export interface Drug {
  id: number;
  name: string;
  e_name: string;
  company: string;
  category: string;
  public_price: number;
  effective_material: string;
  shape: string;
  in_stock: boolean;
  available_quantity: number;
}

export interface AgentResponse {
  success: boolean;
  response: string;
  actions: any[];
  session_id: string | null;
  metadata: Record<string, any>;
}

