// frontend/src/services/api.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const deliveryAddressAPI = {
  // Get all delivery addresses
  getAll: () => api.get('/delivery-addresses/'),
  
  // Get single delivery address
  getById: (id) => api.get(`/delivery-addresses/${id}/`),
  
  // Create new delivery address
  create: (data) => api.post('/delivery-addresses/', data),
  
  // Update delivery address
  update: (id, data) => api.put(`/delivery-addresses/${id}/`, data),
  
  // Delete delivery address
  delete: (id) => api.delete(`/delivery-addresses/${id}/`),
  
  // Validate address
  validateAddress: (address) => 
    api.get('/delivery-addresses/validate_address/', { address }),
  
  // Bulk upload CSV
  bulkUpload: (file, createdBy) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('created_by', createdBy);
    
    return api.post('/delivery-addresses/bulk_upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api;