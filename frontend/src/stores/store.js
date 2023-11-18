import { defineStore } from "pinia";

export const useAuthStore = defineStore({
  id: "auth",
  state: () => ({
    token: localStorage.getItem("token") || null,
    authenticated: localStorage.getItem("authenticated") || false,
  }),
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("token", token);
      this.authenticated = true;
      localStorage.setItem("authenticated", true);
    },
    getToken() {
      return this.token;
    },
    clearToken() {
      this.token = null;
      localStorage.removeItem("token");
      this.authenticated = false;
      localStorage.setItem("authenticated", false);
    },
    getAuthenticated() {
      return this.authenticated;
    },
  },
});
