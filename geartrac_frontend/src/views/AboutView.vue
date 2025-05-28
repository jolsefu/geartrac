<script setup>
import { ref, onMounted } from "vue";

const isVisibleMain = ref(false);

onMounted(async () => {
  setTimeout(() => {
    isVisibleMain.value = true;
  }, 200);
});
</script>

<template>
  <div class="flex items-center justify-center h-screen text-center">
    <Transition name="swipe-right">
      <div v-if="isVisibleMain" class="mr-[-5rem]">
        <img src="/GearTRAC LOGO.png" />
      </div>
    </Transition>

    <Transition name="swipe-left">
      <div v-if="isVisibleMain" class="w-1/2 p-5">
        <h1 class="text-lg text-white text-justify">
          The GearTRAC Gear Management System was created for The Gold Panicles, the
          official student publication of Caraga State University, to streamline the
          management of equipment and supplies. Replacing the paper-based processes with
          features like digital borrower’s slips, multi-level approvals, and real-time
          tracking, the platform supports more organized and accountable gear usage across
          the publication’s activities
        </h1>
      </div>
    </Transition>
  </div>
</template>

<style scoped></style>
