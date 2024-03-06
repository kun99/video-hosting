<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <div class="flex justify-center mt-10">
    <div
      class="w-full max-w-sm p-4 rounded-lg shadow sm:p-6 md:p-8 bg-gray-300 border-gray-700"
    >
      <div class="space-y-6">
        <h5 class="text-xl font-medium text-gray-900 dark:text-white">Login</h5>
        <div>
          <label
            for="username"
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >Username</label
          >
          <input
            name="username"
            v-model="username"
            class="border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            placeholder="Username"
          />
        </div>
        <div>
          <label
            for="password"
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >Password</label
          >
          <input
            name="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-red-500 focus:border-red-500 block w-full p-2.5"
          />
        </div>
        <button
          @click="login"
          class="w-full text-white bg-primary hover:bg-hover focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center"
        >
          Login
        </button>
        <div class="text-sm font-medium text-gray-500 dark:text-gray-300">
          Not registered?
          <RouterLink class="text-blue-700 hover:underline" to="/register">
            Create account
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useAuthStore } from "../stores/store.js";
import NavBar from "../components/NavBar.vue";
export default {
  data() {
    return {
      username: "",
      password: "",
    };
  },
  methods: {
    login() {
      axios
        .post("/auth/login", {
          username: this.username,
          password: this.password,
        })
        .then((response) => {
          const auth = useAuthStore();
          console.log(auth.getAuthenticated());
          auth.setToken(response.data.token);
          console.log(response.data.token);
          this.$router.push("/home");
        })
        .catch((error) => {
          console.error(error);
        });
    },
    // cancel() {
    //   this.$router.push("/");
    // },
  },
  components: { NavBar },
};
</script>
