<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <div class="relative mx-auto pt-20">
    <div
      class="mb-4 text-4xl font-bold tracking-tight text-white text-center xl:px-36 lg:mb-7"
    >
      <h1 class="mb-4 font-extrabold text-white md:text-5xl lg:text-6xl">
        <span
          class="text-transparent bg-clip-text bg-gradient-to-r from-zinc-100 to-rose-800"
          >Easy</span
        >
        Video Sharing.
      </h1>
      <p class="text-lg font-normal lg:text-xl text-gray-400">
        It ain't much but it's easy streaming.
      </p>
    </div>
    <div class="flex flex-row justify-center">
        <RouterLink
          class="text-white hover:bg-hover bg-secondary w-36 focus:ring-4 focus:ring-red-800 font-medium rounded-lg text-base px-6 py-2.5 text-center mb-3"
          to="/register"
        >
          Register?
        </RouterLink>
        <div class="w-3"></div>
        <RouterLink
          class="text-white hover:bg-hover bg-primary w-36 focus:ring-4 focus:ring-red-800 font-medium rounded-lg text-base px-6 py-2.5 text-center mb-3"
          to="/login"
        >
          Login
        </RouterLink>
    </div>
  </div>
</template>
<script>
import NavBar from "../components/NavBar.vue";
import { useAuthStore } from "../stores/store.js";
export default {
  created() {
    const auth = useAuthStore();
  },
  components: { NavBar },
};
</script>
