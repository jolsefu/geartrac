<script setup>
import { ref, watch } from 'vue';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

const props = defineProps({
  notify: { type: Object, required: true },
})

const isVisible = ref(false);

watch(
  props.notify,
  (newNotify) => {
    console.log(newNotify)

    if (newNotify.message && newNotify.messageTitle) {
      isVisible.value = true;
      setTimeout(() => {
        isVisible.value = false;
      }, 7000);
    }
  },
  { deep: true, immediate: true }
);
</script>

<template>
  <transition name="swipe-down">
    <div
      v-if="isVisible"
      class="fixed top-4 left-1/2 transform -translate-x-1/2 w-sm text-white p-4 shadow-md transition-transform duration-500 rounded-md mt-4 z-10"
      :class="{ 'translate-y-0': isVisible, '-translate-y-full': !isVisible }"
    >
      <Alert :variant="notify.messageTitle == 'Error' ? 'destructive' : ''" class="flex flex-col items-start">
        <AlertTitle class="font-bold text-[1rem]">{{ notify.messageTitle }}</AlertTitle>
        <AlertDescription>
          {{ notify.message }}
        </AlertDescription>
      </Alert>
    </div>
  </transition>
</template>

<style scoped>
.fixed {
  z-index: 1000;
}
</style>
