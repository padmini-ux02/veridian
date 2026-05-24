import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (!window.location.pathname.includes('/login')) window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data: { email: string; username: string; full_name: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/me'),
  updateProfile: (data: { full_name?: string; phone?: string }) => api.put('/auth/me', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
};

export const scanAPI = {
  analyze: (data: { scan_type: string; content: string }) => api.post('/scan/analyze', data),
  getHistory: (page = 1, pageSize = 20, scanType?: string) =>
    api.get('/scan/history', { params: { page, page_size: pageSize, scan_type: scanType } }),
  getStats: () => api.get('/scan/stats'),
  getById: (id: string) => api.get(`/scan/${id}`),
};

export const reportAPI = {
  create: (data: { report_type: string; title: string; content: string; description?: string; source?: string }) =>
    api.post('/reports/', data),
  getMyReports: (page = 1) => api.get('/reports/my-reports', { params: { page } }),
  getById: (id: string) => api.get(`/reports/${id}`),
};

export const chatAPI = {
  send: (message: string, scanId?: string) =>
    api.post('/chat/', { message, scan_id: scanId }),
};

export const dashboardAPI = {
  getAlerts: (page = 1, unreadOnly = false) =>
    api.get('/dashboard/alerts', { params: { page, unread_only: unreadOnly } }),
  markRead: (alertIds: string[]) => api.put('/dashboard/alerts/mark-read', { alert_ids: alertIds }),
  markAllRead: () => api.put('/dashboard/alerts/mark-all-read'),
};

export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: (page = 1) => api.get('/admin/users', { params: { page } }),
  toggleUserStatus: (userId: string, isActive: boolean) =>
    api.put(`/admin/users/${userId}/toggle-status`, null, { params: { is_active: isActive } }),
  getReports: (page = 1, status?: string) =>
    api.get('/admin/reports', { params: { page, status } }),
  updateReport: (reportId: string, data: { status: string; admin_notes?: string }) =>
    api.put(`/admin/reports/${reportId}`, data),
  getAlerts: (page = 1) => api.get('/admin/alerts', { params: { page } }),
};

export default api;
