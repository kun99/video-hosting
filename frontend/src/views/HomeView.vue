<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
    <div
      v-for="thumbnail in thumbnails"
      :key="thumbnail[0].metadata.id"
      class="mt-[20px] flex justify-center"
    >
      <div class="flex flex-row">
        <div>
          <img
            :src="thumbnail[0].file"
            @click="clickedVideo(thumbnail[0].metadata.id)"
            class="h-[300px] w-[400px] rounded-lg cursor-pointer"
          />
          <div class="flex flex-col justify-start w-full">
            <div class="flex flex-row">
              <div class="w-4/5">
                <p class="text-white font-bold">
                  {{ thumbnail[0].metadata.title }} -
                  {{ thumbnail[0].metadata.user }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="flex flex-col ml-2 mt-2 items-center">
          <div class="text-white">
            <font-awesome-icon icon="fa-solid fa-eye" />
          </div>
          <div class="text-white">
            {{ thumbnail[0]["views"] }}
          </div>
          <div class="text-white">
            <font-awesome-icon icon="fa-solid fa-heart" />
          </div>
          <div class="text-white">
            {{ thumbnail[0]["likes"] }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useAuthStore } from "../stores/store";
import NavBar from "../components/NavBar.vue";
export default {
  data() {
    return {
      user: "",
      thumbnails: [],
      socket: null,
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
    },
    sortVids() {
      let axiosRequests = [];
      for (let thumbnail of this.thumbnails) {
        axiosRequests.push(
          axios
            .get("/api/views/" + thumbnail[0].metadata.id)
            .then((response) => {
              thumbnail[0]["views"] = response.data.views;
              thumbnail[0]["likes"] = response.data.likes;
            })
        );
      }
      Promise.all(axiosRequests)
        .then(() => {
          this.thumbnails.sort(function (a, b) {
            if (parseInt(a[0]["views"]) < parseInt(b[0]["views"])) return 1;
            if (parseInt(a[0]["views"]) > parseInt(b[0]["views"])) return -1;
            return 0;
          });
          console.log(this.thumbnails);
        })
        .catch((error) => {
          console.error("Error fetching views:", error);
        });
    },
  },
  mounted() {
    setInterval(() => {
      this.sortVids();
    }, 10000);
  },
  beforeMount() {
    axios
      .get("/api/thumbnails")
      .then((response) => {
        this.thumbnails = response.data.thumbnails;
        this.sortVids();
      })
      .catch((error) => {
        console.error("Couldn't fetch thumbnails:", error);
      });
  },
  components: { NavBar },
};
</script>
