<script setup>
import { ref } from "vue";
import Authenticate from "../components/Authenticate.vue";

const isVisible = ref(false);

setTimeout(() => {
  isVisible.value = true;
}, 200);
</script>

<template>
  <Transition name="swipe-up">
    <div v-if="isVisible" class="flex items-center h-screen pt-[8rem] flex-col">
      <Authenticate form-title="Sign Up" />
    </div>
  </Transition>
</template>
