<template>
  <div class="text-white">
    <h1>WebSocket Test</h1>
    <div>
      <label for="message">Message:</label>
      <input type="text" v-model="message" id="message" />
      <button @click="sendMessage">Send</button>
    </div>
    <div>
      <h2>Received Messages:</h2>
      <ul>
        <li v-for="(msg, index) in receivedMessages" :key="index">{{ msg }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import io from "socket.io-client";

export default {
  data() {
    return {
      message: "",
      receivedMessages: [],
    };
  },
  mounted() {
    // Replace 'http://localhost:5000' with your Flask WebSocket server address
    const socket = io.connect("http://localhost:5000");
    socket.on("test_msg", (msg) => {
      console.log(msg)
      this.receivedMessages.push(msg);
    });
  },
  methods: {
    // sendMessage() {
    //   if (this.message) {
    //     // Replace 'http://localhost:5000' with your Flask WebSocket server address
    //     const socket = io.connect("http://localhost:5000");
    //     socket.emit("message", this.message);
    //     this.message = "";
    //   }
    // },
    sendMessage() {
      if (this.message) {
        // Replace 'http://localhost:5000' with your Flask WebSocket server address
        const socket = io.connect("http://localhost:5000");
        socket.emit("test_msg", this.message);
        this.message = "";
      }
    },
  },
};
</script>
