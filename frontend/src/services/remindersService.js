import { api } from './api';

export const remindersService = {
  getReminders: async (status = null) => {
    const params = status ? { status } : {};
    const response = await api.get('/reminders', { params });
    return response.data;
  },

  getReminder: async (id) => {
    const response = await api.get(`/reminders/${id}`);
    return response.data;
  },

  createReminder: async (reminderData) => {
    const response = await api.post('/reminders', reminderData);
    return response.data;
  },

  updateReminder: async (id, updateData) => {
    const response = await api.patch(`/reminders/${id}`, updateData);
    return response.data;
  },

  deleteReminder: async (id) => {
    await api.delete(`/reminders/${id}`);
  },

  processDueReminders: async () => {
    const response = await api.post('/reminders/process');
    return response.data;
  },
};
