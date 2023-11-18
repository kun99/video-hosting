<template>
  <nav class="z-20 top-0 left-0 border-b border-gray-800">
    <NavBar />
  </nav>
  <h1 style="display: flex; justify-content: center">Upload</h1>
  <div class="flex flex-col">
    <div class="flex flex-row items-center justify-center">
      <div class="flex w-1/4 mt-6 mr-5">
        <label
          for="dropzone-file"
          @dragover.prevent
          @dragenter.prevent
          @drop="handleDrop"
          class="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 hover:bg-gray-100"
        >
          <div class="flex flex-col items-center justify-center pt-5 pb-6">
            <svg
              class="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 20 16"
            >
              <path
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
              />
            </svg>
            <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
              <span class="font-semibold">Click to upload</span> or drag and
              drop
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">MP4</p>
          </div>
          <input id="dropzone-file" type="file" class="hidden" />
        </label>
      </div>
      <div class="">
        <label for="title" class="block mb-2 text-sm font-medium text-white"
          >Title:</label
        >
        <textarea
          id="message"
          rows="1"
          v-model="title"
          class="block w-96 p-2.5 text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter title"
        ></textarea>
        <label
          for="description"
          class="block mb-2 text-sm font-medium text-white"
          >Description:</label
        >
        <textarea
          id="message"
          rows="9"
          v-model="desc"
          class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter video description"
        ></textarea>
      </div>
    </div>
    <div class="flex justify-center">
      <div class="flex bg-black w-6/12 justify-end mt-5">
        <RouterLink to="/">
          <button class="text-white mr-2">Cancel</button>
        </RouterLink>
        <button class="text-white ml-2" @click="uploadVideo">OK</button>
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
      instruction: "Drag and drop a video",
      video: null,
      title: "",
      desc: "",
      user: "",
    };
  },
  methods: {
    async handleDrop(event) {
      event.preventDefault();
      this.video = event.dataTransfer.files[0];
      this.instruction = "Video dropped.";
    },
    async uploadVideo() {
      if (this.video && this.video.type.startsWith("video/")) {
        if (this.title && this.desc) {
          const duration = await this.checkVideoDuration();
          if (duration <= 60) {
            await this.uploadVideoToS3();
          } else {
            alert("Video exceeding 60 seconds.");
          }
        } else {
          alert("Missing title or description.");
        }
      } else {
        alert("Missing video file.");
      }
    },
    async checkVideoDuration() {
      return new Promise((resolve, reject) => {
        const videoElement = document.createElement("video");
        videoElement.src = URL.createObjectURL(this.video);
        videoElement.addEventListener("loadedmetadata", () => {
          this.videoDuration = videoElement.duration;
          resolve(this.videoDuration);
        });
        videoElement.addEventListener("error", (error) => {
          reject(error);
        });
      });
    },
    async uploadVideoToS3() {
      const formData = new FormData();
      formData.append("title", this.title);
      formData.append("user", this.user);
      try {
        const response = await axios.post("/api/get_presigned_url", formData);
        const presignedUrl = response.data.url;
        console.log(presignedUrl);
        await axios.put(presignedUrl, this.video, {
          headers: {
            "x-amz-meta-title": this.title,
            "x-amz-meta-id": response.data.id,
            "x-amz-meta-time": response.data.datetime,
            "x-amz-meta-desc": this.desc,
            "Content-Type": "video/mp4",
            Metadata: {
              "x-amz-meta-title": this.title,
              "x-amz-meta-user": this.user,
              "x-amz-meta-id": response.data.id,
              "x-amz-meta-desc": this.desc,
              "x-amz-meta-time": response.data.datetime,
            },
          },
        });
        console.log("Video uploaded successfully");
        await axios.post("/api/tasks", {
          key: "videos/" + this.user + "/" + this.title,
          user: this.user,
          title: this.title,
          desc: this.desc,
          id: response.data.id,
          time: response.data.datetime,
        });
        console.log("Thumbnail fetched");
        await axios.post("/api/initialize", {
          video_id: response.data.id,
        });
        console.log("Added to db");
        window.location = "list";
      } catch (error) {
        console.error("Error uploading video:", error);
      }
    },
  },
  created() {
    //getting username using authentication token
    const auth = useAuthStore();
    axios.get("/api/fetch_username").then((response) => {
      this.user = response.data.name;
    });
    // axios
    //     .post("/api/get_user_using_token", {
    //     token: auth.getToken(),
    // })
    //     .then((response) => {
    //     this.user = response.data.username;
    // })
    //     .catch((error) => {
    //     console.log(error.response.data.message);
    // });
    // axios
    //     .get("/api/fetch_username")
    //     .then((response) => {
    //     this.user = response.data.name;
    //     console.log("user: ", response.data.name);
    //     axios
    //         .post("/api/get_token", {
    //         username: response.data.name,
    //     })
    //         .then((response) => {
    //         const auth = useAuthStore();
    //         auth.setToken(response.data.token);
    //     })
    //         .catch((error) => {
    //         console.error(error);
    //         alert("Login again");
    //         this.$router.push("/");
    //     });
    // })
    //     .catch((error) => {
    //     console.error(error);
    //     alert("Login again");
    //     this.$router.push("/");
    // });
  },
  components: { NavBar },
};
</script>
