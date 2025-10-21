// lib/api.ts - API Client for Django and FastAPI
import axios, { AxiosInstance } from 'axios';

const DJANGO_API = process.env.NEXT_PUBLIC_DJANGO_API || 'http://localhost:8000';
const FASTAPI_API = process.env.NEXT_PUBLIC_FASTAPI_API || 'http://localhost:8001';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'change-this-in-production';

// Django API Client
export const djangoApi: AxiosInstance = axios.create({
  baseURL: DJANGO_API,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

// FastAPI Client
export const fastapi: AxiosInstance = axios.create({
  baseURL: FASTAPI_API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Functions

// Calls
export const getCalls = async (params?: {
  status?: string;
  pharmacy_id?: number;
  page?: number;
  page_size?: number;
}) => {
  const response = await djangoApi.get('/ai-agent/calls/', { params });
  return response.data;
};

export const getCallDetail = async (callId: number) => {
  const response = await djangoApi.get(`/ai-agent/calls/${callId}/`);
  return response.data;
};

export const getCallAudio = (callId: number) => {
  return `${DJANGO_API}/ai-agent/calls/${callId}/audio/`;
};

// Agent
export const processQuery = async (query: string, sessionId?: string) => {
  const response = await fastapi.post('/agent/process', {
    query,
    session_id: sessionId,
  });
  return response.data;
};

export const startCall = async (pharmacyId?: number, userId?: number) => {
  const response = await fastapi.post('/calls/start', {
    pharmacy_id: pharmacyId,
    user_id: userId,
  });
  return response.data;
};

export const endCall = async (sessionId: string) => {
  const response = await fastapi.post(`/calls/${sessionId}/end`, {
    session_id: sessionId,
  });
  return response.data;
};

// Health Check
export const checkHealth = async () => {
  const response = await fastapi.get('/health/');
  return response.data;
};

// Drug Search
export const searchDrugs = async (query: string, limit: number = 10) => {
  const response = await djangoApi.get('/market/ai/drugs/search/', {
    params: { q: query, limit },
  });
  return response.data;
};

