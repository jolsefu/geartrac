<script setup>
import { ref } from "vue";
import { api } from "@/api";

const isVisible = ref(false);

setTimeout(() => {
  isVisible.value = true;
}, 200);
</script>

<template>
  <Transition name="swipe-up">
    <div
      v-if="isVisible"
      class="flex items-center justify-center h-screen text-center flex-col"
    >
      Borrow
    </div>
  </Transition>
</template>
