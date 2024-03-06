<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <div class="w-full">
    <div class="m-6" v-for="thumbnail in thumbnails" :keys="thumbnail">
      <div
        class="flex flex-col items-center bg-white border border-gray-200 rounded-lg shadow md:flex-row hover:bg-gray-100"
      >
        <img
          class="object-cover w-full rounded-t-lg h-96 md:h-auto md:w-48 md:rounded-none md:rounded-l-lg cursor-pointer"
          :src="thumbnail[0].file"
          @click="clickedVideo(thumbnail[0].metadata.id)"
        />
        <div class="flex justify-between p-4 w-full">
          <div class="flex flex-col leading-normal w-7/12">
            <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900">
              {{ thumbnail[0].metadata.title }}
            </h5>
            <p class="mb-3 font-normal text-gray-700">
              {{ thumbnail[0].metadata.desc }}
            </p>
          </div>
          <div class="flex flex-col items-center w-1/12">
            <button
              @click="
                deleteVideo(
                  thumbnail[0].metadata.title,
                  thumbnail[0].metadata.id
                )
              "
              class="cursor-pointer bg-red-300 w-8 rounded-md"
            >
              X
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from "../components/NavBar.vue";
import { useAuthStore } from "../stores/store";
import axios from "axios";
export default {
  data() {
    return {
      user: "",
      thumbnails: [],
    };
  },
  methods: {
    clickedVideo(id) {
      axios
        .post("/api/set_videod", {
          id: id,
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
      this.$router.push("/playback");
    },
    deleteVideo(title, id) {
      axios
        .delete("/api/delete", {
          data: {
            username: this.user,
            title: title,
            id: id,
          },
        })
        .then((response) => {
          axios.delete("/api/remove_views/${id}");
          alert(response.data.message);
          this.$router.go("");
        })
        .catch((error) => {
          console.error("Couldn't delete thumbnail:", error);
        });
    },
  },
  mounted() {
    const authStore = useAuthStore();
    //fetches username using token stored in pinia
    axios
      .post("/auth/fetch_username", {
        token: authStore.getToken(),
      })
      .then((response) => {
        this.user = response.data.name;
        axios
          .post("/api/my_thumbnails", {
            username: response.data.name,
          })
          .then((response) => {
            this.thumbnails = response.data.thumbnails;
          })
          .catch((error) => {
            console.error("Couldn't fetch thumbnails:", error);
          });
      })
      .catch((error) => {
        console.error("Couldn't retrieve username:", error);
      });
  },
  components: { NavBar },
};
</script>
