import api from './axios'

export const ticketsApi = {
  getList(params) {
    return api.get('/tickets/', { params }).then(r => r.data)
  },
  getById(id) {
    return api.get(`/tickets/${id}`).then(r => r.data)
  },
  create(data) {
    return api.post('/tickets/', data).then(r => r.data)
  },
  update(id, data) {
    return api.put(`/tickets/${id}`, data).then(r => r.data)
  },
  delete(id) {
    return api.delete(`/tickets/${id}`)
  },
  batchDelete(ids) {
    return api.post('/tickets/batch-delete', { ids })
  },
  bulkUpdate(ids, data) {
    return api.put('/tickets/batch-update', { ids, ...data })
  },
}

export const categoriesApi = {
  getList() {
    return api.get('/categories/').then(r => r.data)
  },
}

export const commentsApi = {
  getList(ticketId) {
    return api.get(`/tickets/${ticketId}/comments/`).then(r => r.data)
  },
  create(ticketId, data) {
    return api.post(`/tickets/${ticketId}/comments/`, data).then(r => r.data)
  },
  delete(ticketId, commentId) {
    return api.delete(`/tickets/${ticketId}/comments/${commentId}`)
  },
}

export const authApi = {
  login(email, password) {
    return api.post('/auth/login', { email, password }).then(r => r.data)
  },
  register(name, email, password) {
    return api.post('/auth/register', { name, email, password, role: 'user' }).then(r => r.data)
  },
  getMe() {
    return api.get('/auth/me').then(r => r.data)
  },
}

export const usersApi = {
  getList() {
    return api.get('/users/').then(r => r.data.items || r.data)
  },
}
