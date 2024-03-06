import { defineStore } from "pinia";

export const useAuthStore = defineStore({
  id: "auth",
  state: () => ({
    token: null,
    authenticated: false
  }),
  actions: {
    setToken(token) {
      this.token = token;
      this.authenticated = true;
    },
    getToken() {
      return this.token;
    },
    clearToken() {
      this.token = null;
      this.authenticated = false;
    },
    getAuthenticated() {
      return this.authenticated;
    },
  },
  persist: true
});
