<template>
  <div
    class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4 border-gray-200"
  >
    <div class="flex items-center">
      <img src="@/assets/toktik.png" class="h-8 mr-3" alt="toktik logo" />
      <span class="self-center text-2xl font-semibold whitespace-nowrap">
        <div v-if="userStore.getAuthenticated()">
          <RouterLink to="/home">
            <button class="text-white">TokTik</button>
          </RouterLink>
        </div>
        <div v-else>
          <RouterLink to="/">
            <button class="text-white">TokTik</button>
          </RouterLink>
        </div>
      </span>
    </div>
    <div v-if="userStore.getAuthenticated()" class="flex md:order-2">
      <div class="relative">
        <button
          @click="toggleDropdown"
          class="bg-primary text-white font-bold py-2 px-4 mr-2 rounded hover:bg-red-600"
        >
          <font-awesome-icon icon="fas fa-bell" />
        </button>

        <div
          v-show="isDropdownOpen"
          @click.away="closeDropdown"
          class="absolute mt-2 w-64 bg-white border rounded shadow-lg cursor-pointer"
        >
          <li
            v-for="notification in notificationList"
            class="p-4 list-none"
            @click="clickedNoti(notification)"
          >
            {{ notification.notification }}
          </li>
        </div>
      </div>
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
import io from "socket.io-client";
import { useAuthStore } from "../stores/store";

export default {
  data() {
    return {
      isDropdownOpen: false,
      store: null,
      notificationList: [],
    };
  },
  created() {
    this.store = useAuthStore();
  },
  mounted() {
    this.notificationList = [];
    this.getNotifications();
    this.setupSocket();
  },
  computed: {
    userStore() {
      console.log(this.store.getAuthenticated());
      return this.store;
    },
  },
  methods: {
    setupSocket() {
      this.socket = io.connect("http://localhost:5000");
      this.socket.on("update_notifications", (notifications) => {
        this.notificationList = notifications.notifications;
      });
    },
    getNotifications() {
      axios.get("/api/get-notifications").then((response) => {
        console.log(response.data.notifications);
        this.notificationList = response.data.notifications;
      });
    },
    toggleDropdown() {
      this.isDropdownOpen = !this.isDropdownOpen;
    },
    closeDropdown() {
      this.isDropdownOpen = false;
    },
    clickedNoti(notification) {
      console.log(`Notification clicked: ${notification.video_id}`);
      axios
        .post("/api/set_videod", {
          id: notification.video_id,
          i: 0,
        })
        .then((response) => {
          this.$router.push("/playback");
        })
        .catch((error) => {
          console.error(error);
          alert("It ain't good");
          this.$router.push("/home");
        });
      console.log(notification.notification_id);
      axios.delete("/api/delete-notification/" + notification.notification_id);
    },
    logout() {
      axios
        .post("api/logout")
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
