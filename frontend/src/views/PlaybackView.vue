<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <div class="flex justify-center">
    <div class="flex flex-col items-start">
      <div class="flex items-center">
        <div class="mx-4">
          <video
            class="video-js"
            ref="videoPlayer"
          ></video>
        </div>
      </div>
      <div class="flex flex-col justify-start ml-5 w-full">
        <div class="flex flex-row">
          <div class="w-5/6">
            <p class="text-white font-bold text-2xl">{{ this.title }}</p>
          </div>
        </div>
        <div class="flex flex-row">
          <div class="w-5/6">
            <p class="text-white">{{ this.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "../stores/store";
import axios from "axios";
import videojs from "video.js";
import NavBar from "../components/NavBar.vue";
export default {
  data() {
    return {
      id: "",
      user: "",
      video: "",
      videos: [],
      title: "",
      desc: "",
      i: 0,
      m3u8: "",
      player: null,
      authenticated: false,
    };
  },
  methods: {
    clickedVideo(id, title) {
      axios
        .post("/api/set_videod", {
          id: id,
          title: title,
          i: this.i,
        })
        .catch((error) => {
          console.error(error);
          alert("It ain't good");
          this.$router.push("/home");
        });
      this.$router.go();
    },
    initVideo() {
      this.player = videojs(this.$refs.videoPlayer, {
        controls: true,
        autoplay: true,
        sources: [
          {
            src: this.m3u8,
            type: "application/x-mpegURL",
          },
        ],
      });
    },
  },
  mounted() {
    this.authenticated = useAuthStore().getAuthenticated();
    axios
      .get("/api/videod")
      .then((response) => {
        this.id = response.data.id;
        this.title = response.data.title;
        this.i = response.data.i;
        this.increaseViews();
        //m3u8
        axios
          .post("/api/hls", {
            title: this.title,
            id: this.id,
          })
          .then((response) => {
            console.log(response.data);
            this.desc = response.data.metadata.desc;
            this.m3u8 = response.data.m3u8;
            this.initVideo();
            this.player.on("pause", () => {
              this.$refs.videoPlayer.pause();
            });
            this.player.on("play", () => {
              this.$refs.videoPlayer.play();
            });
          })
          .catch((error) => {
            console.error("Couldn't fetch video:", error);
          });
      })
      .catch((error) => {
        console.error("Couldn't fetch videos:", error);
      });
    axios
      .get("/api/videos")
      .then((response) => {
        this.videos = response.data.videos;
        console.log(this.videos);
      })
      .catch((error) => {
        console.error("Couldn't fetch videos:", error);
      });
  },
  beforeDestroy() {
    if (this.player) {
      this.player.dispose();
    }
  },
  components: { NavBar },
};
</script>
