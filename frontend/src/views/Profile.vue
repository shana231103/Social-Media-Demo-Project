<template>
  <div class="flex max-w-[1250px] mx-auto min-h-screen relative">
    <!-- Left Sidebar -->
    <Sidebar />

    <!-- Main Feed/Profile Column -->
    <main class="flex-grow max-w-[600px] min-h-screen border-r border-border-main flex flex-col">
      <!-- Profile Header -->
      <div class="backdrop-blur-md bg-black/65 sticky top-0 z-10 border-b border-border-main p-4 flex items-center gap-5">
        <button class="text-white hover:text-accent font-bold text-xl cursor-pointer" @click="router.back()">←</button>
        <div>
          <h1 class="text-lg font-bold text-white leading-tight">{{ profileUser?.display_name || 'Đang tải...' }}</h1>
          <span class="text-gray-500 text-xs">
            {{ tweetsStore.profileTweets.length }} Bài viết
          </span>
        </div>
      </div>

      <!-- Banner and Avatar -->
      <div class="relative">
        <div class="h-[150px] bg-zinc-800"></div>
        <div class="absolute -bottom-[60px] left-5 z-2">
          <img :src="profileUser?.avatar_url" class="w-[120px] h-[120px] rounded-full object-cover border-4 border-black bg-zinc-800" alt="Avatar" />
        </div>
      </div>

      <!-- Profile Metadata and Actions -->
      <div class="p-5 border-b border-border-main mt-[55px] flex flex-col gap-3">
        <!-- Action Buttons Row -->
        <div class="flex justify-end gap-2.5">
          <!-- Chat Button for other users -->
          <button 
            v-if="!isCurrentUser" 
            class="bg-zinc-900 border border-border-main hover:bg-zinc-800 text-white px-5 py-2 rounded-full font-bold text-sm transition-all" 
            @click="openChat"
          >
            Nhắn tin
          </button>
          
          <!-- Friend/Relationship Action Button -->
          <button 
            v-if="!isCurrentUser" 
            class="px-5 py-2 rounded-full font-bold text-sm transition-all"
            :class="friendshipStatus === 'accepted' ? 'bg-zinc-900 border border-border-main hover:bg-red-950/20 hover:text-red-500 text-white' : 'bg-accent hover:bg-accent-hover text-white'"
            @click="handleFriendshipAction"
          >
            {{ friendshipButtonText }}
          </button>
        </div>

        <!-- User Information -->
        <div class="flex flex-col mt-1.5">
          <h2 class="text-xl font-extrabold text-white leading-tight">
            {{ profileUser?.display_name }}
          </h2>
          <span class="text-gray-500 text-sm">
            @{{ profileUser?.username }}
          </span>
        </div>

        <!-- Joined Date -->
        <div class="flex items-center gap-1.5 text-sm text-gray-500">
          <span>📅</span>
          <span>Đã tham gia {{ formatJoinedDate(profileUser?.created_at) }}</span>
        </div>

        <!-- Friends Count -->
        <div class="flex gap-5 text-sm mt-1.5">
          <span>
            <strong class="text-white">{{ friendsCount }}</strong>
            <span class="text-gray-500 ml-1">Bạn bè</span>
          </span>
        </div>
      </div>

      <!-- Tab Selectors -->
      <div class="flex border-b border-border-main">
        <button
          class="flex-1 py-4 text-center font-bold border-b-4 hover:bg-white/[0.03] hover:text-white transition-all"
          :class="activeTab === 'tweets' ? 'text-white border-accent' : 'text-gray-500 border-transparent'"
          @click="switchTab('tweets')"
        >
          Bài đăng
        </button>
        <button
          class="flex-1 py-4 text-center font-bold border-b-4 hover:bg-white/[0.03] hover:text-white transition-all"
          :class="activeTab === 'liked' ? 'text-white border-accent' : 'text-gray-500 border-transparent'"
          @click="switchTab('liked')"
        >
          Đã thích
        </button>
      </div>

      <!-- Tweets List -->
      <div class="flex flex-col">
        <div v-for="tweet in tweetsStore.profileTweets" :key="tweet.id" class="border-b border-border-main">
          <!-- Tweet Card -->
          <div class="p-4 flex gap-4 hover:bg-white/[0.02] transition-colors cursor-pointer" @click="toggleComments(tweet.id)">
            <img :src="tweet.user.avatar_url" class="w-10 h-10 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" />
            <div class="flex-grow flex flex-col gap-2">
              <div class="flex items-center gap-1.5 text-sm">
                <span class="font-bold text-white">{{ tweet.user.display_name }}</span>
                <span class="text-gray-500">@{{ tweet.user.username }}</span>
                <span class="text-gray-500 text-xs">·</span>
                <span class="text-gray-500">{{ formatTime(tweet.created_at) }}</span>
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

          <!-- Inline Comments drawer -->
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
                <img :src="comment.user.avatar_url" class="w-8 h-8 rounded-full object-cover bg-zinc-800 shrink-0" alt="Avatar" />
                <div class="flex flex-col gap-1 flex-grow">
                  <div class="flex items-center gap-1.5 text-xs">
                    <span class="font-bold text-white">{{ comment.user.display_name }}</span>
                    <span class="text-gray-500">@{{ comment.user.username }}</span>
                    <span class="text-gray-500">·</span>
                    <span class="text-gray-500">{{ formatTime(comment.created_at) }}</span>
                  </div>
                  <div class="text-[14px] text-white whitespace-pre-wrap break-words">{{ comment.content }}</div>
                </div>
              </div>
              <div v-if="!tweetsStore.comments[tweet.id] || tweetsStore.comments[tweet.id].length === 0" class="text-gray-500 text-xs text-center py-2">
                Chưa có phản hồi nào.
              </div>
            </div>
          </div>
        </div>

        <div v-if="tweetsStore.profileTweets.length === 0" class="p-10 text-center text-gray-500">
          Không có bài viết nào để hiển thị.
        </div>
      </div>
    </main>

    <!-- Right Sidebar -->
    <aside class="w-[350px] p-3 pl-6 flex flex-col gap-4 sticky top-0 h-screen max-lg:hidden">
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
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useTweetsStore } from '../stores/tweets';
import { useChatStore } from '../stores/chat';
import { api } from '../stores/auth';
import Sidebar from '../components/Sidebar.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const tweetsStore = useTweetsStore();
const chatStore = useChatStore();

const profileUser = ref(null);
const activeTab = ref('tweets');

const activeCommentTweetId = ref(null);
const newCommentText = ref('');
const commenting = ref(false);
const loadingComments = ref(false);

const isCurrentUser = computed(() => {
  return route.params.id === authStore.user?.id;
});

const friendsCount = ref(0);

// Detect friendship status to show correct action buttons
const friendshipStatus = computed(() => {
  const targetId = route.params.id;
  
  // Check if accepted friend
  const isFriend = chatStore.friends.some(f => f.id === targetId);
  if (isFriend) return 'accepted';

  // Check if incoming pending request
  const hasIncoming = chatStore.requests.some(r => r.sender_id === targetId);
  if (hasIncoming) return 'incoming';

  return 'none';
});

const friendshipButtonText = computed(() => {
  const status = friendshipStatus.value;
  if (status === 'accepted') return 'Hủy kết bạn';
  if (status === 'incoming') return 'Đồng ý kết bạn';
  return 'Kết bạn';
});

// Load profile user and tweets
const loadProfile = async () => {
  const userId = route.params.id;
  try {
    const res = await api.get(`/auth/user/${userId}`);
    profileUser.value = res.data;
  } catch (err) {
    console.error('Error fetching user profile:', err);
  }

  // Load friends count from backend
  try {
    const countRes = await api.get(`/friendships/user/${userId}/friends/count`);
    friendsCount.value = countRes.data;
  } catch (err) {
    console.error('Error fetching friends count:', err);
    friendsCount.value = 0;
  }

  activeTab.value = 'tweets';
  await tweetsStore.fetchUserTweets(userId);
  await chatStore.fetchFriends();
  await chatStore.fetchRequests();
};

onMounted(loadProfile);

watch(() => route.params.id, loadProfile);

const switchTab = async (tab) => {
  activeTab.value = tab;
  const userId = route.params.id;
  if (tab === 'tweets') {
    await tweetsStore.fetchUserTweets(userId);
  } else {
    await tweetsStore.fetchLikedTweets(userId);
  }
};

const handleFriendshipAction = async () => {
  const targetId = route.params.id;
  const status = friendshipStatus.value;
  
  try {
    if (status === 'accepted') {
      if (confirm('Bạn có chắc chắn muốn hủy kết bạn?')) {
        await chatStore.removeFriend(targetId);
        alert('Đã hủy kết bạn.');
      }
    } else if (status === 'incoming') {
      await chatStore.acceptFriendRequest(targetId);
      alert('Đã đồng ý kết bạn!');
    } else {
      await chatStore.sendFriendRequest(targetId);
      alert('Đã gửi lời mời kết bạn!');
    }
    await chatStore.fetchFriends();
    await chatStore.fetchRequests();
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi thao tác kết bạn');
  }
};

const openChat = () => {
  chatStore.activeFriendId = route.params.id;
  router.push({ name: 'Messages' });
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

const formatJoinedDate = (dateStr) => {
  if (!dateStr) return 'Tháng 6, 2026';
  const date = new Date(dateStr);
  return `Tháng ${date.getMonth() + 1} năm ${date.getFullYear()}`;
};
</script>
