<template>
  <div class="min-h-screen bg-black flex items-center justify-center p-4">
    <div class="w-full max-w-[450px] bg-black border border-border-main rounded-2xl p-10 flex flex-col gap-6">
      <div class="text-6xl font-black text-center text-white">𝕏</div>
      <h2 class="text-3xl font-extrabold text-white text-left">Đăng ký tài khoản mới</h2>
      <form @submit.prevent="handleRegister" class="flex flex-col gap-5">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-500" for="username">Tên đăng nhập (username)</label>
          <input
            id="username"
            type="text"
            v-model="username"
            required
            class="bg-black border border-border-main rounded p-4 text-white text-base focus:border-accent focus:outline-none transition-all"
            placeholder="Ví dụ: shana23"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-500" for="displayName">Tên hiển thị (display name)</label>
          <input
            id="displayName"
            type="text"
            v-model="displayName"
            required
            class="bg-black border border-border-main rounded p-4 text-white text-base focus:border-accent focus:outline-none transition-all"
            placeholder="Ví dụ: Shana Nguyễn"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-500" for="email">Địa chỉ Email</label>
          <input
            id="email"
            type="email"
            v-model="email"
            required
            class="bg-black border border-border-main rounded p-4 text-white text-base focus:border-accent focus:outline-none transition-all"
            placeholder="Email liên hệ"
          />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-sm font-semibold text-gray-500" for="password">Mật khẩu (tối thiểu 6 ký tự)</label>
          <input
            id="password"
            type="password"
            v-model="password"
            required
            class="bg-black border border-border-main rounded p-4 text-white text-base focus:border-accent focus:outline-none transition-all"
            placeholder="Mật khẩu bảo mật"
          />
        </div>
        <div v-if="authStore.error" class="text-red-500 text-sm">
          {{ authStore.error }}
        </div>
        <button type="submit" class="bg-accent hover:bg-accent-hover text-white py-3 rounded-full font-bold transition-all disabled:opacity-50 mt-2" :disabled="loading">
          {{ loading ? 'Đang đăng ký...' : 'Đăng ký' }}
        </button>
      </form>
      <div class="text-center text-gray-500 text-sm mt-2">
        Đã có tài khoản? 
        <router-link to="/login" class="text-accent hover:underline ml-1">Đăng nhập</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const displayName = ref('');
const email = ref('');
const password = ref('');
const loading = ref(false);

const handleRegister = async () => {
  loading.value = true;
  try {
    const success = await authStore.register(
      username.value,
      email.value,
      displayName.value,
      password.value
    );
    if (success) {
      alert('Đăng ký thành công! Hãy đăng nhập bằng tài khoản vừa tạo.');
      router.push({ name: 'Login' });
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>
