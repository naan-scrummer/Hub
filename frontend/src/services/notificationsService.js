import { api } from './api';

export const notificationsService = {
  async getNotifications(status = null) {
    const params = status && status.toLowerCase() !== 'all' ? { status } : {};
    const response = await api.get('/notifications', { params });
    return response.data;
  },

  async markAsRead(id) {
    const response = await api.post(`/notifications/${id}/read`);
    return response.data;
  },

  async markAllAsRead() {
    const response = await api.post('/notifications/read-all');
    return response.data;
  },

  async createNotification(data) {
    const response = await api.post('/notifications', data);
    return response.data;
  }
};
