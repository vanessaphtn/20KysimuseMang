<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue';

</script>

<template>
  <!--Background video from: https://www.pexels.com/video/abstract-video-4990240/ by: Luis Quintero -->
  <div class="video-container">
    <video autoplay loop muted playsinline class="background-video">
      <source src="@/assets/background.mp4" type="video/mp4" />
      Your browser does not support the video tag.
    </video>

    <div class="content">
      <header>
        <Navbar />
      </header>

      <main>
        <RouterView />
      </main>
    </div>
  </div>
</template>



<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Jacquard+12&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Tiny5&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Jersey+10&display=swap');
.video-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  z-index: -1;
}

.background-video {
  position:fixed;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: translate(-50%, -50%);
}

.content {
  position: relative;
  z-index: 1;
  color: white;
  text-align: center;
  padding-top: 50px;
  min-height: 100vh; /* Vähemalt ekraani kõrgus */
}
</style>