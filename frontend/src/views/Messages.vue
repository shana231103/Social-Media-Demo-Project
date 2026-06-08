<template>
  <div class="flex max-w-[1250px] mx-auto min-h-screen relative">
    <!-- Left Sidebar -->
    <Sidebar />

    <!-- Chat Dashboard (Split View) -->
    <main class="flex flex-grow h-screen max-w-[975px]">
      <!-- Left List Pane: Friend Contacts -->
      <section class="w-[350px] border-r border-border-main flex flex-col h-full shrink-0">
        <div class="p-[18px] px-5 border-b border-border-main">
          <h2 class="text-xl font-extrabold text-white">Tin nhắn</h2>
        </div>
        <div class="flex-grow overflow-y-auto">
          <div
            v-for="friend in chatStore.friends"
            :key="friend.id"
            class="flex items-center gap-3 p-4 px-5 cursor-pointer border-b border-border-main/50 hover:bg-bg-hover transition-colors"
            :class="{ 'bg-accent/8': chatStore.activeFriendId === friend.id }"
            @click="selectFriend(friend.id)"
          >
            <img :src="friend.avatar_url" class="w-10 h-10 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" />
            <div class="flex flex-col overflow-hidden">
              <span class="font-bold text-[15px] text-white truncate">{{ friend.display_name }}</span>
              <span class="text-[13px] text-gray-500 truncate">@{{ friend.username }}</span>
            </div>
            <span v-if="chatStore.activeFriendId === friend.id" class="ml-auto text-accent text-xl">💬</span>
          </div>

          <div v-if="chatStore.friends.length === 0" class="p-10 text-center text-gray-500 text-sm">
            Chưa có bạn bè nào. 
            <p class="text-xs mt-1.5 text-gray-500">
              Tìm kiếm người dùng ở Trang chủ và gửi lời mời kết bạn để nhắn tin!
            </p>
          </div>
        </div>
      </section>

      <!-- Right Chat Window Pane -->
      <section class="flex-grow flex flex-col h-full bg-black">
        <!-- Active Conversation Chat Window -->
        <div v-if="activeFriend" class="flex flex-col h-full">
          <!-- Active Contact Header -->
          <div class="flex items-center gap-3 p-3 px-5 border-b border-border-main cursor-pointer hover:bg-bg-hover transition-colors" @click="goToProfile(activeFriend.id)">
            <img :src="activeFriend.avatar_url" class="w-10 h-10 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" />
            <div class="flex flex-col">
              <span class="font-bold text-[15px] text-white">{{ activeFriend.display_name }}</span>
              <span class="text-xs text-gray-500">@{{ activeFriend.username }}</span>
            </div>
            <span class="text-xs text-accent ml-auto">Xem hồ sơ</span>
          </div>

          <!-- Messages Scroller Log -->
          <div class="flex-grow p-5 overflow-y-auto flex flex-col gap-3" ref="messagesContainer">
            <div v-if="chatStore.loading" class="text-center text-gray-500 text-sm mt-10">
              Đang tải lịch sử tin nhắn...
            </div>
            <template v-else>
              <div
                v-for="msg in chatStore.messages"
                :key="msg.id"
                class="flex w-full"
                :class="{ 'justify-end': msg.sender_id === authStore.user?.id }"
              >
                <div 
                  class="max-w-[65%] p-3 px-4 rounded-[18px] text-white flex flex-col gap-1"
                  :class="msg.sender_id === authStore.user?.id ? 'bg-accent rounded-br-[4px]' : 'bg-zinc-800 rounded-bl-[4px]'"
                >
                  <span class="text-[15px] leading-relaxed break-words">{{ msg.content }}</span>
                  <span class="text-[10px] text-white/60 align-self-end mt-0.5">
                    {{ formatTime(msg.created_at) }}
                  </span>
                </div>
              </div>
              
              <div v-if="chatStore.messages.length === 0" class="text-center text-gray-500 text-sm mt-10">
                Bắt đầu cuộc trò chuyện. Hãy gửi lời chào đầu tiên!
              </div>
            </template>
          </div>

          <!-- Message Input Box -->
          <div class="p-4 px-5 border-t border-border-main flex gap-3 items-center">
            <input
              v-model="messageText"
              type="text"
              class="flex-grow bg-zinc-900 border border-transparent rounded-full py-3 px-5 text-white text-[15px] focus:bg-black focus:border-accent focus:outline-none transition-all"
              placeholder="Bắt đầu tin nhắn mới..."
              @keyup.enter="handleSendMessage"
            />
            <button
              class="bg-transparent border-none text-2xl cursor-pointer transition-transform hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!messageText.trim()"
              @click="handleSendMessage"
            >
              🚀
            </button>
          </div>
        </div>

        <!-- Chat Inactive State (Default Dashboard landing) -->
        <div v-else class="flex-grow flex flex-col justify-center items-center text-center p-10 max-w-[400px] mx-auto gap-2.5">
          <div class="text-5xl mb-2.5">✉️</div>
          <h2 class="text-2xl font-extrabold text-white">Chọn một cuộc trò chuyện</h2>
          <p class="text-gray-500 text-sm leading-relaxed">Hãy chọn người bạn từ danh sách liên hệ để bắt đầu chia sẻ tin nhắn trong thời gian thực!</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';
import Sidebar from '../components/Sidebar.vue';

const router = useRouter();
const authStore = useAuthStore();
const chatStore = useChatStore();

const messageText = ref('');
const messagesContainer = ref(null);

const activeFriend = computed(() => {
  return chatStore.friends.find((f) => f.id === chatStore.activeFriendId) || null;
});

const selectFriend = async (friendId) => {
  await chatStore.fetchHistory(friendId);
  nextTick(scrollToBottom);
};

const handleSendMessage = () => {
  if (!messageText.value.trim() || !chatStore.activeFriendId) return;
  chatStore.sendMessage(chatStore.activeFriendId, messageText.value);
  messageText.value = '';
  nextTick(() => {
    setTimeout(scrollToBottom, 50);
  });
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

onMounted(async () => {
  await chatStore.fetchFriends();
  chatStore.initWebSocket();
  
  if (chatStore.activeFriendId) {
    await chatStore.fetchHistory(chatStore.activeFriendId);
    nextTick(scrollToBottom);
  }
});

watch(
  () => chatStore.messages,
  () => {
    nextTick(scrollToBottom);
  },
  { deep: true }
);

const goToProfile = (userId) => {
  router.push(`/profile/${userId}`);
};

const formatTime = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
};
</script>
