<template>
  <div class="flex max-w-[1250px] mx-auto min-h-screen relative">
    <!-- Left Sidebar -->
    <Sidebar />

    <!-- Central Feed -->
    <main class="flex-grow max-w-[600px] min-h-screen border-r border-border-main flex flex-col">
      <div class="backdrop-blur-md bg-black/65 sticky top-0 z-10 border-b border-border-main p-4">
        <h1 class="text-xl font-bold text-white">Trang chủ</h1>
      </div>

      <!-- Create Tweet Box -->
      <div class="p-4 flex gap-4 border-b border-border-main">
        <img :src="authStore.user?.avatar_url" class="w-10 h-10 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" />
        <div class="flex-grow flex flex-col gap-3">
          <textarea
            v-model="newTweetContent"
            class="w-full resize-none bg-transparent text-xl leading-normal text-white placeholder-gray-500 border-none outline-none min-h-[80px]"
            placeholder="Chuyện gì đang xảy ra?!"
            maxlength="280"
          ></textarea>
          <div class="flex justify-between items-center border-t border-[#2f3336] pt-3">
            <span class="text-gray-500 text-xs">
              {{ 280 - newTweetContent.length }} ký tự còn lại
            </span>
            <button
              class="bg-accent hover:bg-accent-hover text-white px-5 py-2.5 rounded-full font-bold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!newTweetContent.trim() || posting"
              @click="submitTweet"
            >
              {{ posting ? 'Đang đăng...' : 'Đăng' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="tweetsStore.loading && tweetsStore.tweets.length === 0" class="p-10 text-center text-gray-500">
        Đang tải bài viết...
      </div>

      <!-- Tweets List -->
      <div v-else class="flex flex-col">
        <div v-for="tweet in tweetsStore.tweets" :key="tweet.id" class="border-b border-border-main">
          <!-- Tweet Card -->
          <div class="p-4 flex gap-4 hover:bg-white/[0.02] transition-colors cursor-pointer" @click="toggleComments(tweet.id)">
            <img :src="tweet.user.avatar_url" class="w-10 h-10 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" @click.stop="goToProfile(tweet.user.id)" />
            <div class="flex-grow flex flex-col gap-2">
              <div class="flex items-center gap-1.5 text-sm">
                <span class="font-bold text-white hover:underline" @click.stop="goToProfile(tweet.user.id)">
                  {{ tweet.user.display_name }}
                </span>
                <span class="text-gray-500" @click.stop="goToProfile(tweet.user.id)">
                  @{{ tweet.user.username }}
                </span>
                <span class="text-gray-500 text-xs">·</span>
                <span class="text-gray-500" :title="new Date(tweet.created_at).toLocaleString()">
                  {{ formatTime(tweet.created_at) }}
                </span>
              </div>
              <div class="text-[15px] leading-normal text-white whitespace-pre-wrap break-words">{{ tweet.content }}</div>
              
              <!-- Tweet Actions -->
              <div class="flex gap-10 mt-2.5 text-gray-500">
                <!-- Comment Button -->
                <button class="flex items-center gap-2 text-[13px] text-gray-500 hover:text-accent transition-colors bg-transparent border-none outline-none cursor-pointer" @click.stop="toggleComments(tweet.id)">
                  <span>💬 {{ tweet.comments_count }}</span>
                </button>
                <!-- Like Button -->
                <button 
                  class="flex items-center gap-2 text-[13px] transition-colors bg-transparent border-none outline-none cursor-pointer" 
                  :class="tweet.is_liked ? 'text-red-500 hover:text-red-600' : 'text-gray-500 hover:text-accent'" 
                  @click.stop="tweetsStore.toggleLike(tweet.id)"
                >
                  <span>❤️ {{ tweet.likes_count }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Inline Comments Area -->
          <div v-if="activeCommentTweetId === tweet.id" class="border-t border-border-main p-4 bg-zinc-950/20">
            <!-- Comment Input -->
            <div class="flex gap-3 mb-4">
              <img :src="authStore.user?.avatar_url" class="w-8 h-8 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" />
              <div class="flex-grow flex flex-col gap-2">
                <input
                  v-model="newCommentText"
                  type="text"
                  class="bg-black border border-border-main rounded p-2 text-white text-sm focus:border-accent focus:outline-none w-full"
                  placeholder="Viết phản hồi của bạn..."
                  @keyup.enter="submitComment(tweet.id)"
                />
                <div class="flex justify-end">
                  <button
                    class="bg-accent hover:bg-accent-hover text-white px-4 py-1.5 rounded-full font-bold text-xs transition-all disabled:opacity-50"
                    :disabled="!newCommentText.trim() || commenting"
                    @click="submitComment(tweet.id)"
                  >
                    {{ commenting ? 'Đang gửi...' : 'Phản hồi' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Comments List -->
            <div v-if="loadingComments" class="text-center text-gray-500 text-xs p-2">
              Đang tải bình luận...
            </div>
            <div v-else class="flex flex-col gap-4">
              <div v-for="comment in tweetsStore.comments[tweet.id]" :key="comment.id" class="flex gap-3 text-sm">
                <img :src="comment.user.avatar_url" class="w-8 h-8 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" @click="goToProfile(comment.user.id)" />
                <div class="flex flex-col gap-1 flex-grow">
                  <div class="flex items-center gap-1.5 text-xs">
                    <span class="font-bold text-white" @click="goToProfile(comment.user.id)">{{ comment.user.display_name }}</span>
                    <span class="text-gray-500" @click="goToProfile(comment.user.id)">@{{ comment.user.username }}</span>
                    <span class="text-gray-500">·</span>
                    <span class="text-gray-500">{{ formatTime(comment.created_at) }}</span>
                  </div>
                  <div class="text-[14px] text-white whitespace-pre-wrap break-words">{{ comment.content }}</div>
                </div>
              </div>
              <div v-if="!tweetsStore.comments[tweet.id] || tweetsStore.comments[tweet.id].length === 0" class="text-gray-500 text-xs text-center py-2">
                Chưa có phản hồi nào. Hãy là người đầu tiên bình luận!
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Right Sidebar -->
    <aside class="w-[350px] p-3 pl-6 flex flex-col gap-4 sticky top-0 h-screen max-lg:hidden">
      <!-- Search Widget -->
      <div class="bg-bg-card rounded-full py-3 px-5 flex items-center gap-3 border border-transparent focus-within:bg-black focus-within:border-accent">
        <span class="text-gray-500">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          class="w-full bg-transparent border-none text-white text-sm outline-none placeholder-gray-500"
          placeholder="Tìm kiếm người dùng..."
          @input="handleSearch"
        />
      </div>

      <!-- Search Results -->
      <div v-if="searchQuery.trim()" class="bg-bg-card rounded-2xl p-4 flex flex-col gap-3">
        <h2 class="text-lg font-extrabold text-white">Kết quả tìm kiếm</h2>
        <div v-for="user in chatStore.searchResults" :key="user.id" class="flex justify-between items-center py-2 border-b border-zinc-800/50 last:border-0">
          <div class="flex items-center gap-2.5 cursor-pointer" @click="goToProfile(user.id)">
            <img :src="user.avatar_url" class="w-8 h-8 rounded-full object-cover bg-zinc-800" alt="Avatar" />
            <div class="flex flex-col">
              <span class="font-bold text-sm text-white">{{ user.display_name }}</span>
              <span class="text-xs text-gray-500">@{{ user.username }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button class="bg-accent hover:bg-accent-hover text-white px-3 py-1 rounded-full font-bold text-xs" @click="sendFriendRequest(user.id)">
              Kết bạn
            </button>
            <button class="bg-white text-black hover:bg-gray-200 px-3 py-1 rounded-full font-bold text-xs" @click="openChat(user.id)">
              Chat
            </button>
          </div>
        </div>
        <div v-if="chatStore.searchResults.length === 0" class="text-gray-500 text-xs text-center py-2">
          Không tìm thấy người dùng phù hợp.
        </div>
      </div>

      <!-- Friend Requests Widget -->
      <div v-if="chatStore.requests.length > 0" class="bg-bg-card rounded-2xl p-4 flex flex-col gap-3">
        <h2 class="text-lg font-extrabold text-white">Lời mời kết bạn</h2>
        <div v-for="req in chatStore.requests" :key="req.sender_id" class="flex justify-between items-center py-2 border-b border-zinc-800/50 last:border-0">
          <div class="flex items-center gap-2.5 cursor-pointer" @click="goToProfile(req.sender_id)">
            <img :src="req.sender.avatar_url" class="w-8 h-8 rounded-full object-cover bg-zinc-800" alt="Avatar" />
            <div class="flex flex-col">
              <span class="font-bold text-sm text-white">{{ req.sender.display_name }}</span>
              <span class="text-xs text-gray-500">@{{ req.sender.username }}</span>
            </div>
          </div>
          <button class="bg-accent hover:bg-accent-hover text-white px-3.5 py-1.5 rounded-full font-bold text-xs" @click="chatStore.acceptFriendRequest(req.sender_id)">
            Đồng ý
          </button>
        </div>
      </div>

      <!-- Who to Follow -->
      <div class="bg-bg-card rounded-2xl p-4 flex flex-col gap-3">
        <h2 class="text-lg font-extrabold text-white">Gợi ý kết bạn</h2>
        <div class="text-gray-500 text-xs leading-relaxed">
          Sử dụng thanh tìm kiếm để tìm và gửi lời mời kết bạn đến người khác.
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useTweetsStore } from '../stores/tweets';
import { useChatStore } from '../stores/chat';
import Sidebar from '../components/Sidebar.vue';

const router = useRouter();
const authStore = useAuthStore();
const tweetsStore = useTweetsStore();
const chatStore = useChatStore();

const newTweetContent = ref('');
const posting = ref(false);

const activeCommentTweetId = ref(null);
const newCommentText = ref('');
const commenting = ref(false);
const loadingComments = ref(false);

const searchQuery = ref('');

onMounted(async () => {
  await tweetsStore.fetchFeed();
  await chatStore.fetchRequests();
});

const submitTweet = async () => {
  if (!newTweetContent.value.trim()) return;
  posting.value = true;
  try {
    const success = await tweetsStore.postTweet(newTweetContent.value);
    if (success) {
      newTweetContent.value = '';
    }
  } catch (err) {
    console.error(err);
  } finally {
    posting.value = false;
  }
};

const toggleComments = async (tweetId) => {
  if (activeCommentTweetId.value === tweetId) {
    activeCommentTweetId.value = null;
  } else {
    activeCommentTweetId.value = tweetId;
    newCommentText.value = '';
    loadingComments.value = true;
    await tweetsStore.fetchComments(tweetId);
    loadingComments.value = false;
  }
};

const submitComment = async (tweetId) => {
  if (!newCommentText.value.trim()) return;
  commenting.value = true;
  try {
    const success = await tweetsStore.addComment(tweetId, newCommentText.value);
    if (success) {
      newCommentText.value = '';
    }
  } catch (err) {
    console.error(err);
  } finally {
    commenting.value = false;
  }
};

const handleSearch = () => {
  chatStore.searchUsers(searchQuery.value);
};

const sendFriendRequest = async (userId) => {
  try {
    await chatStore.sendFriendRequest(userId);
    alert('Đã gửi lời mời kết bạn!');
    searchQuery.value = '';
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi gửi yêu cầu kết bạn');
  }
};

const openChat = (userId) => {
  chatStore.activeFriendId = userId;
  router.push({ name: 'Messages' });
};

const goToProfile = (userId) => {
  router.push(`/profile/${userId}`);
};

const formatTime = (dateStr) => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);

  if (diffMins < 1) return 'vừa xong';
  if (diffMins < 60) return `${diffMins} phút trước`;
  if (diffHours < 24) return `${diffHours} giờ trước`;
  return date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' });
};
</script>
