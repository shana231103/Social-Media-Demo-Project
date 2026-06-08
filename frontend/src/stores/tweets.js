import { defineStore } from 'pinia';
import { api } from './auth';

export const useTweetsStore = defineStore('tweets', {
  state: () => ({
    tweets: [], // Home feed tweets
    profileTweets: [], // Profile page tweets
    comments: {},
    loading: false,
    error: null,
  }),
  actions: {
    async fetchFeed() {
      this.loading = true;
      try {
        const res = await api.get('/tweets');
        this.tweets = res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi tải dòng thời gian';
      } finally {
        this.loading = false;
      }
    },
    async fetchUserTweets(userId) {
      this.loading = true;
      try {
        const res = await api.get(`/tweets/user/${userId}`);
        this.profileTweets = res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi tải bài viết người dùng';
      } finally {
        this.loading = false;
      }
    },
    async fetchLikedTweets(userId) {
      this.loading = true;
      try {
        const res = await api.get(`/tweets/liked/${userId}`);
        this.profileTweets = res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi tải bài viết đã thích';
      } finally {
        this.loading = false;
      }
    },
    async postTweet(content) {
      try {
        const res = await api.post('/tweets', { content });
        this.tweets.unshift(res.data);
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi đăng bài viết';
        throw err;
      }
    },
    async toggleLike(tweetId) {
      // Snappy Optimistic UI Updates
      const tweet = this.tweets.find((t) => t.id === tweetId) || this.profileTweets.find((t) => t.id === tweetId);
      if (tweet) {
        tweet.is_liked = !tweet.is_liked;
        tweet.likes_count += tweet.is_liked ? 1 : -1;
      }
      try {
        await api.post(`/tweets/${tweetId}/like`);
      } catch (err) {
        // Rollback if failure
        if (tweet) {
          tweet.is_liked = !tweet.is_liked;
          tweet.likes_count += tweet.is_liked ? 1 : -1;
        }
        this.error = err.response?.data?.detail || 'Lỗi thích bài viết';
      }
    },
    async fetchComments(tweetId) {
      try {
        const res = await api.get(`/tweets/${tweetId}/comments`);
        this.comments[tweetId] = res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi tải bình luận';
      }
    },
    async addComment(tweetId, content) {
      try {
        const res = await api.post(`/tweets/${tweetId}/comments`, { content });
        if (!this.comments[tweetId]) {
          this.comments[tweetId] = [];
        }
        this.comments[tweetId].push(res.data);

        // Update comments count on the parent tweet
        const tweet = this.tweets.find((t) => t.id === tweetId) || this.profileTweets.find((t) => t.id === tweetId);
        if (tweet) {
          tweet.comments_count += 1;
        }
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lỗi gửi bình luận';
        throw err;
      }
    }
  }
});
