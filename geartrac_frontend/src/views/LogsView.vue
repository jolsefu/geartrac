<script setup>
import { ref, reactive, onMounted } from "vue";
import Notify from "@/components/Notify.vue";

const isVisible = ref(false);

const notify = reactive({
  messageTitle: "",
  message: "",
});

onMounted(() => {
  setTimeout(() => {
    isVisible.value = true;
  }, 200);
});
</script>

<template>
  <Notify :notify="notify" />

  <Transition name="swipe-up">
    <div
      v-if="isVisible"
      class="h-screen text-center flex justify-center w-full items-center"
    >
      <h1 class="">LogsVIEW</h1>
    </div>
  </Transition>
</template>
