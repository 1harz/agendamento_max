// API service for communicating with backend

const API_BASE_URL = '/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // GET request
  async get(endpoint) {
    return this.request(endpoint, {
      method: 'GET'
    });
  }

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }

  // Appointment endpoints
  async getAppointments() {
    return this.get('/appointments');
  }

  async getAppointment(id) {
    return this.get(`/appointments/${id}`);
  }

  async createAppointment(appointmentData) {
    return this.post('/appointments', appointmentData);
  }

  async updateAppointment(id, appointmentData) {
    return this.put(`/appointments/${id}`, appointmentData);
  }

  async deleteAppointment(id) {
    return this.delete(`/appointments/${id}`);
  }

  async completeAppointment(id) {
    return this.post(`/appointments/${id}/complete`);
  }

  async createOccurrence(appointmentId, occurrenceData) {
    return this.post(`/appointments/${appointmentId}/occurrence`, occurrenceData);
  }

  // AI Assistant endpoints
  async sendChatMessage(message, context = null) {
    return this.post('/ai/chat', {
      message,
      context
    });
  }

  async getRecommendations(excludedAppointmentId = null) {
    const params = excludedAppointmentId 
      ? `?excluded_appointment_id=${excludedAppointmentId}` 
      : '';
    return this.get(`/ai/recommendations${params}`);
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;