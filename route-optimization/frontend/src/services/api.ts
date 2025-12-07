import axios from 'axios';
import { MailItem, Route, TrainingLog, TrafficData } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const mailItemsAPI = {
  getAll: () => api.get<MailItem[]>('/mail-items/'),
  createManual: (data: {
    tracking_number: string;
    recipient_name: string;
    address: string;
    city?: string;
    postal_code: string;
    priority?: 'urgent' | 'regular';
    latitude?: number;
    longitude?: number;
  }) => api.post('/mail-items/create_manual/', data),
  uploadCSV: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/mail-items/upload_csv/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  updatePriority: (id: number, priority: 'urgent' | 'regular') =>
    api.patch(`/mail-items/${id}/update_priority/`, { priority }),
};

export const routesAPI = {
  getAll: () => api.get<Route[]>('/routes/'),
  getById: (id: number) => api.get<Route>(`/routes/${id}/`),
  optimize: (mail_item_ids: number[], route_name: string) =>
    api.post('/routes/optimize/', { mail_item_ids, route_name }),
  getTrafficData: (id: number) => api.get<TrafficData[]>(`/routes/${id}/traffic_data/`),
};

export const trainingAPI = {
  getLatest: () => api.get<TrainingLog[]>('/training-logs/latest/'),
};

export default api;