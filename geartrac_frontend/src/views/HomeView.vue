<script setup>
import { ref, onMounted } from "vue";
import { isAuthenticated, userDetails } from "@/auth";

const isVisibleWelcome = ref(false);
const isVisibleMain = ref(false);

onMounted(() => {
  if (isAuthenticated) {
    setTimeout(() => {
      isVisibleWelcome.value = true;
    }, 300);

    setTimeout(() => {
      isVisibleWelcome.value = false;
    }, 2000);

    setTimeout(() => {
      isVisibleMain.value = true;
    }, 3000);
  } else {
    setTimeout(() => {
      isVisibleMain.value = true;
    }, 200);
  }
});
</script>

<template>
  <div class="flex items-center justify-center h-screen text-center flex-col">
    <Transition name="swipe-down">
      <div v-if="isVisibleWelcome">
        <h1 class="text-xl text-white font-bold">
          Welcome, {{ userDetails.first_name }}
        </h1>
      </div>
    </Transition>

    <Transition name="swipe-down">
      <h1 v-if="isVisibleMain" class="text-8xl text-white font-bold">GearTRAC</h1>
    </Transition>

    <Transition name="swipe-up">
      <div v-if="isVisibleMain">
        <h1 class="text-lg text-white mt-4">
          Developed Exclusively for The Gold Panicles
        </h1>
      </div>
    </Transition>
  </div>
</template>

<style scoped></style>
