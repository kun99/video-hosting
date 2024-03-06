import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/store";
import NavBar from "@/components/NavBar.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/home",
      component: NavBar,
      name: "home",
      meta: {
        requiresAuth: true,
      },
      component: () => import("../views/HomeView.vue"),
    },
    {
      path: "/list",
      component: NavBar,
      name: "list",
      meta: {
        requiresAuth: true,
      },
      component: () => import("../views/ListView.vue"),
    },
    {
      path: "/upload",
      component: NavBar,
      name: "upload",
      meta: {
        requiresAuth: true,
      },
      component: () => import("../views/UploadView.vue"),
    },
    {
      path: "/",
      name: "landing",
      meta: {
        requiresGuest: true,
      },
      component: () => import("../views/LandingView.vue"),
    },
    {
      path: "/login",
      component: NavBar,
      name: "login",
      meta: {
        requiresGuest: true,
      },
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/register",
      component: NavBar,
      name: "register",
      meta: {
        requiresGuest: true,
      },
      component: () => import("../views/RegisterView.vue"),
    },
    {
      path: "/playback",
      component: NavBar,
      name: "playback",
      meta: {
        requiresAuth: true,
      },
      component: () => import("../views/PlaybackView.vue"),
    },
  ],
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some((x) => x.meta.requiresAuth);
  const requiresGuest = to.matched.some((x) => x.meta.requiresGuest);
  const isLoggedin = authStore.getAuthenticated();
  if (requiresAuth && !isLoggedin) {
    next("/login");
  } else if (requiresGuest && isLoggedin) {
    next("/home");
  }  else {
    next();
  }
});

export default router;
