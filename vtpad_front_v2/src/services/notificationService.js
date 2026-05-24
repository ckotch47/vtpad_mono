import api from '@/plugins/axios'

export const notificationService = {
  list: () => api.get('/api/v1/notification'),
  unreadCount: () => api.get('/api/v1/notification/unread-count'),
  markRead: (id) => api.put(`/api/v1/notification/${id}/read`),
  markAllRead: () => api.put('/api/v1/notification/read-all'),
}
