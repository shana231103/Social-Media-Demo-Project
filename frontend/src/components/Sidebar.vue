<template>
  <aside class="w-[75px] md:w-[275px] px-3 py-4 flex flex-col justify-between h-screen sticky top-0 border-r border-border-main">
    <div class="flex flex-col gap-5 flex-grow">
      <div class="px-3 py-2 flex items-center">
        <div class="text-3xl font-black text-white cursor-pointer select-none transition-transform hover:scale-105" @click="router.push('/')">𝕏</div>
      </div>
      <nav class="flex flex-col gap-2 mt-2">
        <router-link to="/" class="flex items-center gap-5 px-4 py-3 rounded-full text-xl font-semibold text-[#e7e9ea] hover:bg-zinc-900/80 transition-colors" :class="{ 'text-white font-bold': route.name === 'Home' }">
          <span>🏠 <span class="max-md:hidden">Trang chủ</span></span>
        </router-link>
        <router-link to="/messages" class="flex items-center gap-5 px-4 py-3 rounded-full text-xl font-semibold text-[#e7e9ea] hover:bg-zinc-900/80 transition-colors" :class="{ 'text-white font-bold': route.name === 'Messages' }">
          <span>✉️ <span class="max-md:hidden">Tin nhắn</span></span>
        </router-link>
        <router-link :to="`/profile/${authStore.user?.id}`" class="flex items-center gap-5 px-4 py-3 rounded-full text-xl font-semibold text-[#e7e9ea] hover:bg-zinc-900/80 transition-colors" :class="{ 'text-white font-bold': route.name === 'Profile' && route.params.id === authStore.user?.id }">
          <span>👤 <span class="max-md:hidden">Cá nhân</span></span>
        </router-link>
      </nav>
    </div>

    <div class="flex items-center gap-3 p-3 rounded-full hover:bg-zinc-900 cursor-pointer mb-4 group transition-colors" @click="handleLogout" title="Click để Đăng xuất">
      <img :src="authStore.user?.avatar_url" class="w-10 h-10 rounded-full object-cover bg-zinc-800" alt="Avatar" />
      <div class="flex flex-col overflow-hidden max-md:hidden">
        <span class="font-bold text-sm truncate text-white">{{ authStore.user?.display_name }}</span>
        <span class="text-xs text-gray-500 truncate">@{{ authStore.user?.username }}</span>
      </div>
      <span class="ml-auto text-xs text-red-500 font-bold opacity-0 group-hover:opacity-100 transition-opacity max-md:hidden">Đăng xuất</span>
    </div>
  </aside>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const chatStore = useChatStore();

const handleLogout = () => {
  if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
    chatStore.closeWebSocket();
    authStore.logout();
    router.push({ name: 'Login' });
  }
};
</script>
