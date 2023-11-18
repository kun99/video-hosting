<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <div class="flex justify-center">
    <div class="flex flex-col items-start">
      <div class="flex items-center">
        <div class="text-white cursor-pointer" @click="navigate('left')">
          &#8249;
        </div>
        <div class="mx-4">
          <video
            class="video-js"
            ref="videoPlayer"
            @ended="navigate('right')"
          ></video>
        </div>
        <div class="text-white cursor-pointer" @click="navigate('right')">
          &#8250;
        </div>
      </div>
      <div class="flex flex-col justify-start ml-5 w-full">
        <div class="flex flex-row">
          <div class="w-5/6">
            <p class="text-white font-bold text-2xl">{{ this.title }}</p>
          </div>
          <div class="w-1/6">
            <p class="text-white">Views: {{ this.views }}</p>
          </div>
        </div>
        <div class="flex flex-row">
          <div class="w-5/6">
            <p class="text-white">{{ this.desc }}</p>
          </div>
          <div class="w-1/6">
            <button @click="increaseLikes" class="text-white bg-primary">
              Likes
              {{ this.likes }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="py-8">
    <div class="max-w-2xl mx-auto px-4">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-white">Comments</h2>
      </div>
      <div class="mb-6">
        <div
          class="py-2 px-4 mb-4 bg-white rounded-lg rounded-t-lg border border-gray-200"
        >
          <label for="comment" class="sr-only">Your comment</label>
          <textarea
            v-model="comment"
            rows="6"
            class="px-0 w-full text-sm text-gray-900 border-0 focus:ring-0 focus:outline-none"
            placeholder="Write a comment..."
            required
          ></textarea>
        </div>
        <button
          @click="submitComment"
          class="inline-flex items-center py-2.5 px-4 text-xs font-medium text-center text-white bg-gray-700 rounded-lg hover:bg-gray-800"
        >
          Post comment
        </button>
      </div>
      <article
        v-for="comment in comments"
        :key="comment.id"
        class="p-6 text-base rounded-lg bg-gray-900 mb-1"
      >
        <footer class="flex justify-between items-center mb-2">
          <div class="flex items-center">
            <p
              class="inline-flex items-center mr-3 text-sm text-white font-semibold"
            >
              {{ comment.user }}
            </p>
          </div>
        </footer>
        <p class="text-gray-500 dark:text-gray-400">
          {{ comment.comment }}
        </p>
      </article>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "../stores/store";
import axios from "axios";
import videojs from "video.js";
import io from "socket.io-client";
import NavBar from "../components/NavBar.vue";
export default {
  data() {
    return {
      id: "",
      user: "",
      video: "",
      videos: [],
      comments: [],
      title: "",
      desc: "",
      views: "",
      likes: "",
      i: 0,
      m3u8: "",
      comment: "",
      player: null,
      socket: null,
      authenticated: false,
    };
  },
  methods: {
    setupSocket() {
      this.socket = io.connect("http://localhost:5000");
      this.socket.on("update_views", (views) => {
        this.views = views.views;
      });
      this.socket.on("update_likes", (likes) => {
        this.likes = likes.likes;
      });
    },
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
    navigate(direction) {
      if (direction === "right") {
        if (this.i >= this.videos.length - 1) {
          this.i = 0;
        } else {
          this.i++;
        }
      } else {
        this.i = this.i > 0 ? this.i - 1 : this.videos.length - 1;
      }
      this.clickedVideo(
        this.videos[this.i][0].metadata.id,
        this.videos[this.i][0].metadata.title
      );
    },
    increaseViews() {
      try {
        axios.post("/api/increment/" + this.id).then((response) => {
          this.views = response.data.views;
          console.log(this.views);
        });
      } catch (error) {
        console.error("Couldn't increment views.");
      }
    },
    increaseLikes() {
      try {
        axios.post("/api/like/" + this.id).then((response) => {
          this.likes = response.data.likes;
        });
      } catch (error) {
        console.error("Couldn't increment likes.");
      }
    },
    async getLikes() {
      const response = await axios.get("/api/views/" + this.id);
      this.likes = response.data.likes;
      this.views = response.data.views;
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
    getComments() {
      axios.get("/api/get-comments/" + this.id).then((response) => {
        console.log("Attempting to get commetns");
        this.comments = response.data.comments;
        console.log("Retrieved " + this.comments[0]);
      });
    },
    submitComment() {
      console.log(this.comment);
      axios
        .post("/api/add-comment", { video: this.id, comment: this.comment })
        .then((response) => {
          console.log(response.data.message);
        });
      this.comment = "";
      this.getComments();
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
            this.setupSocket();
            this.getLikes();
            this.initVideo();
            this.getComments();
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
    setInterval(() => {
      this.getComments();
    }, 10000);
    // setInterval(() => {
    //   this.getLikes();
    // }, 10000);
  },
  beforeDestroy() {
    if (this.player) {
      this.player.dispose();
    }
  },
  components: { NavBar },
};
</script>
