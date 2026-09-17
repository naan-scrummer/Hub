import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
  profile: () => api.get('/auth/profile'),
}

export const dashboardApi = {
  get: () => api.get('/dashboard'),
}

export const attendanceApi = {
  getSubjects: () => api.get('/attendance/subjects'),
  getSummary: () => api.get('/attendance/summary'),
  getSubject: (subjectId) => api.get(`/attendance/${subjectId}`),
  sync: (studentId) => api.post('/attendance/sync', { student_id: studentId }),
}

export const academicsApi = {
  get: () => api.get('/academics'),
  sync: (studentId) => api.post('/academics/sync', { student_id: studentId }),
}

export const examinationsApi = {
  get: () => api.get('/examinations'),
  sync: () => api.post('/examinations/sync', {}),
}

export const announcementsApi = {
  get: (params) => api.get('/announcements', { params }),
  getSources: () => api.get('/announcements/sources'),
  sync: (sourceId) => api.post('/announcements/sync', { source_id: sourceId }),
}

export const placementsApi = {
  getOpportunities: () => api.get('/placements/opportunities'),
  getContributions: () => api.get('/placements/contributions'),
  getMyContributions: () => api.get('/placements/my-contributions'),
  createContribution: (data) => api.post('/placements/contributions', data),
  sync: () => api.post('/placements/sync', {}),
}

export const studyMaterialsApi = {
  get: (params) => api.get('/materials', { params }),
  getBySubject: (subjectId) => api.get(`/materials/subject/${subjectId}`),
  getById: (materialId) => api.get(`/materials/${materialId}`),
  create: (data) => api.post('/materials', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getMyUploads: () => api.get('/materials/my-uploads'),
}

export const assignmentsApi = {
  get: () => api.get('/assignments'),
  getBySubject: (subjectId) => api.get(`/assignments/subject/${subjectId}`),
  create: (data) => api.post('/assignments', data),
  update: (assignmentId, data) => api.patch(`/assignments/${assignmentId}`, data),
  complete: (assignmentId) => api.post(`/assignments/${assignmentId}/complete`),
  delete: (assignmentId) => api.delete(`/assignments/${assignmentId}`),
  getMaterials: (assignmentId) => api.get(`/assignments/${assignmentId}/materials`),
}

export const remindersApi = {
  get: (status = null) => {
    const params = status ? { status } : {};
    return api.get('/reminders', { params });
  },
  getById: (id) => api.get(`/reminders/${id}`),
  create: (data) => api.post('/reminders', data),
  update: (id, data) => api.patch(`/reminders/${id}`, data),
  delete: (id) => api.delete(`/reminders/${id}`),
  process: () => api.post('/reminders/process'),
}

export const notificationsApi = {
  get: (params) => api.get('/notifications', { params }),
  markRead: (notificationId) => api.post(`/notifications/${notificationId}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
}