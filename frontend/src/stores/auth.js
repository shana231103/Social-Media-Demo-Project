import { defineStore } from 'pinia';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Interceptor to attach Authorization JWT token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export { api };

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || '',
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username_or_email, password) {
      try {
        this.error = null;
        const res = await api.post('/auth/login', { username_or_email, password });
        this.token = res.data.access_token;
        this.user = {
          id: res.data.user_id,
          username: res.data.username,
          display_name: res.data.display_name,
          avatar_url: res.data.avatar_url,
        };
        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại.';
        throw err;
      }
    },
    async register(username, email, display_name, password) {
      try {
        this.error = null;
        await api.post('/auth/register', { username, email, display_name, password });
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
        throw err;
      }
    },
    logout() {
      this.token = '';
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },
    async fetchMe() {
      if (!this.token) return;
      try {
        const res = await api.get('/auth/me');
        this.user = res.data;
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (err) {
        this.logout();
      }
    }
  }
});
