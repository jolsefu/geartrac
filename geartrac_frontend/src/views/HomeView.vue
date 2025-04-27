<script setup>
import { ref } from "vue";

const isVisible = ref(false);

setTimeout(() => {
  isVisible.value = true;
}, 200);
</script>

<template>
  <div class="flex items-center justify-center h-screen text-center flex-col">
    <Transition name="swipe-down">
      <h1 v-if="isVisible" class="text-8xl text-white font-bold">GearTRAC</h1>
    </Transition>

    <Transition name="swipe-up">
      <h1 v-if="isVisible" class="text-lg text-white mt-4">
        Developed Exclusively for The Gold Panicles
      </h1>
    </Transition>
  </div>
</template>

<style scoped></style>
