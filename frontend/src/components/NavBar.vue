<template>
  <div
    class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4 border-gray-200"
  >
    <div class="flex items-center">
      <span class="self-center text-2xl font-semibold whitespace-nowrap">
        <div v-if="userStore.getAuthenticated()">
          <RouterLink to="/home">
            <button class="text-white">streameasy</button>
          </RouterLink>
        </div>
        <div v-else>
          <RouterLink to="/">
            <button class="text-white">streameasy</button>
          </RouterLink>
        </div>
      </span>
    </div>
    <div v-if="userStore.getAuthenticated()" class="flex md:order-2">
      <button
        class="text-white bg-red-500 hover:bg-hover focus:ring-4 focus:outline-none focus:ring-red-700 font-medium rounded-lg text-sm px-4 py-2 text-center mr-3"
        @click="logout"
      >
        Logout
      </button>
    </div>
    <div
      v-if="userStore.getAuthenticated()"
      class="items-center justify-between hidden w-full md:flex md:w-auto md:order-1"
    >
      <ul
        class="flex flex-col p-4 md:p-0 mt-4 font-medium rounded-lg md:flex-row md:space-x-8 md:mt-0"
      >
        <li>
          <RouterLink
            to="/list"
            class="blockt text-white rounded hover:bg-gray-100 md:hover:bg-transparent md:hover:text-red-500 md:p-0 md:dark:hover:text-red-500"
            >My Videos</RouterLink
          >
        </li>
        <li>
          <RouterLink
            to="/upload"
            class="block text-white rounded hover:bg-gray-100 md:hover:bg-transparent md:hover:text-red-500 md:p-0 md:dark:hover:text-red-500"
          >
            <button>Upload</button>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useAuthStore } from "../stores/store";

export default {
  data() {
    return {
      store: null,
    };
  },
  created() {
    this.store = useAuthStore();
  },
  computed: {
    userStore() {
      console.log(this.store.getAuthenticated());
      return this.store;
    },
  },
  methods: {
    logout() {
      axios
        .post("/auth/logout")
        .then((response) => {
          this.store.clearToken();
          this.$router.push("/");
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
};
</script>
