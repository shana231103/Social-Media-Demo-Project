<template>
  <div class="min-h-screen bg-black flex items-center justify-center p-4">
    <div class="w-full max-w-[450px] bg-black border border-border-main rounded-2xl p-10 flex flex-col gap-6">
      <div class="text-6xl font-black text-center text-white">𝕏</div>
      <h2 class="text-3xl font-extrabold text-white text-left">Đăng nhập vào X Clone</h2>
      <form @submit.prevent="handleLogin" class="flex flex-col gap-5">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-500" for="identity">Tên đăng nhập hoặc Email</label>
          <input
            id="identity"
            type="text"
            v-model="identity"
            required
            class="bg-black border border-border-main rounded p-4 text-white text-base focus:border-accent focus:outline-none transition-all"
            placeholder="username hoặc email"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-500" for="password">Mật khẩu</label>
          <input
            id="password"
            type="password"
            v-model="password"
            required
            class="bg-black border border-border-main rounded p-4 text-white text-base focus:border-accent focus:outline-none transition-all"
            placeholder="Mật khẩu"
          />
        </div>
        <div v-if="authStore.error" class="text-red-500 text-sm">
          {{ authStore.error }}
        </div>
        <button type="submit" class="bg-accent hover:bg-accent-hover text-white py-3 rounded-full font-bold transition-all disabled:opacity-50 mt-2" :disabled="loading">
          {{ loading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
        </button>
      </form>
      <div class="text-center text-gray-500 text-sm mt-2">
        Chưa có tài khoản? 
        <router-link to="/register" class="text-accent hover:underline ml-1">Đăng ký</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';

const router = useRouter();
const authStore = useAuthStore();
const chatStore = useChatStore();

const identity = ref('');
const password = ref('');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  try {
    const success = await authStore.login(identity.value, password.value);
    if (success) {
      chatStore.initWebSocket();
      router.push({ name: 'Home' });
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>
