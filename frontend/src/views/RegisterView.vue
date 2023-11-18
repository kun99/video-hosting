<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar/>
  </nav>
  <div class="flex justify-center mt-10">
    <div
      class="w-full max-w-sm p-4 rounded-lg shadow sm:p-6 md:p-8 bg-gray-300 border-gray-700"
    >
      <div class="space-y-6">
        <h5 class="text-xl font-medium text-gray-900">Register</h5>
        <div>
          <label
            for="username"
            class="block mb-2 text-sm font-medium text-gray-900"
            >Username</label
          >
          <input
            v-model="username"
            type="username"
            class="border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-red-500 focus:border-red-500 block w-full p-2.5"
            placeholder="Username"
            required
          />
        </div>
        <div>
          <label
            for="password"
            class="block mb-2 text-sm font-medium text-gray-900"
            >Password</label
          >
          <input
            type="password"
            v-model="password"
            placeholder="••••••••"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-red-500 focus:border-red-500 block w-full p-2.5"
            required
          />
        </div>
        <button
          @click="register"
          class="w-full text-white bg-primary hover:bg-hover focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center"
        >
          Register
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import NavBar from "../components/NavBar.vue";
export default {
    data() {
        return {
            username: "",
            password: "",
        };
    },
    methods: {
        register() {
            axios
                .post("/api/register", {
                username: this.username,
                password: this.password,
            })
                .then((response) => {
                console.log(response.data);
                this.$router.push("/success");
            })
                .catch((error) => {
                console.error(error);
            });
        },
        cancel() {
            this.$router.push("/");
        },
    },
    components: { NavBar }
};
</script>