<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from './stores/auth';
import { useChatStore } from './stores/chat';

const authStore = useAuthStore();
const chatStore = useChatStore();

onMounted(async () => {
  // Sync details and start WebSocket connection if user is logged in
  if (authStore.isAuthenticated) {
    await authStore.fetchMe();
    chatStore.initWebSocket();
  }
});
</script>
