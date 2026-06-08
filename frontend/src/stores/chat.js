import { defineStore } from 'pinia';
import { api } from './auth';

export const useChatStore = defineStore('chat', {
  state: () => ({
    friends: [],
    requests: [],
    searchResults: [],
    messages: [], // Messages of active conversation channel
    ws: null,
    activeFriendId: null,
    loading: false,
  }),
  actions: {
    async fetchFriends() {
      try {
        const res = await api.get('/friendships/friends');
        this.friends = res.data;
      } catch (err) {
        console.error('Error fetching friends:', err);
      }
    },
    async fetchRequests() {
      try {
        const res = await api.get('/friendships/requests');
        this.requests = res.data;
      } catch (err) {
        console.error('Error fetching requests:', err);
      }
    },
    async searchUsers(query) {
      if (!query.trim()) {
        this.searchResults = [];
        return;
      }
      try {
        const res = await api.get('/friendships/search', { params: { q: query } });
        this.searchResults = res.data;
      } catch (err) {
        console.error('Error searching users:', err);
      }
    },
    async sendFriendRequest(friendId) {
      try {
        await api.post(`/friendships/request/${friendId}`);
        await this.fetchRequests();
        return true;
      } catch (err) {
        console.error('Error sending request:', err);
        throw err;
      }
    },
    async acceptFriendRequest(requesterId) {
      try {
        await api.post(`/friendships/accept/${requesterId}`);
        await this.fetchRequests();
        await this.fetchFriends();
        return true;
      } catch (err) {
        console.error('Error accepting request:', err);
        throw err;
      }
    },
    async removeFriend(friendId) {
      try {
        await api.delete(`/friendships/remove/${friendId}`);
        await this.fetchFriends();
        if (this.activeFriendId === friendId) {
          this.activeFriendId = null;
          this.messages = [];
        }
      } catch (err) {
        console.error('Error removing friend:', err);
      }
    },
    async fetchHistory(friendId) {
      this.activeFriendId = friendId;
      this.loading = true;
      try {
        const res = await api.get(`/messages/history/${friendId}`);
        this.messages = res.data;
      } catch (err) {
        console.error('Error fetching history:', err);
      } finally {
        this.loading = false;
      }
    },
    initWebSocket() {
      if (this.ws) {
        this.ws.close();
      }
      const token = localStorage.getItem('token');
      if (!token) return;

      const wsUrl = `ws://127.0.0.1:8000/api/messages/ws/${token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.type === 'chat_message') {
            const msg = parsed.data;
            // Append message if it belongs to the active conversation channel
            if (
              msg.sender_id === this.activeFriendId || 
              msg.receiver_id === this.activeFriendId
            ) {
              if (!this.messages.some((m) => m.id === msg.id)) {
                this.messages.push(msg);
              }
            }
          }
        } catch (err) {
          console.error('Error parsing WS message:', err);
        }
      };

      this.ws.onclose = () => {
        // Automatically attempt reconnect after 3 seconds if user is still logged in
        setTimeout(() => {
          if (localStorage.getItem('token')) {
            this.initWebSocket();
          }
        }, 3000);
      };
    },
    sendMessage(receiverId, content) {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(
          JSON.stringify({
            receiver_id: receiverId,
            content: content,
          })
        );
      } else {
        // Fallback to REST API if socket connection isn't ready
        api.post('/messages', { receiver_id: receiverId, content }).then((res) => {
          if (!this.messages.some((m) => m.id === res.data.id)) {
            this.messages.push(res.data);
          }
        });
      }
    },
    closeWebSocket() {
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
    }
  }
});
