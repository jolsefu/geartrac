<script setup>
import { ref } from "vue";
import { isAuthenticated, userDetails } from "@/auth";

const isVisible = ref(false);

setTimeout(() => {
  isVisible.value = true;
}, 200);
</script>

<template>
  <div class="flex items-center justify-center h-screen text-center flex-col">
    <Transition name="swipe-down">
      <div v-if="isVisible">
        <div v-if="isAuthenticated" class="mb-5">
          <span>Welcome, {{ userDetails.first_name }}</span>
        </div>
        <h1 v-if="isVisible" class="text-8xl text-white font-bold">GearTRAC</h1>
      </div>
    </Transition>

    <Transition name="swipe-up">
      <div v-if="isVisible">
        <h1 class="text-lg text-white mt-4">
          Developed Exclusively for The Gold Panicles
        </h1>
      </div>
    </Transition>
  </div>
</template>

<style scoped></style>
