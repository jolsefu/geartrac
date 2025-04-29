<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  notify: { type: Object, required: true },
});

const notifications = ref([]);

function removeNotification(index) {
  notifications.value.splice(index, 1);
}

watch(
  props.notify,
  (newNotify) => {
    if (newNotify.message && newNotify.messageTitle) {
      notifications.value.unshift({ ...newNotify });

      props.notify.success = false;
      props.notify.error = false;
      props.notify.message = false;

      setTimeout(() => {
        removeNotification(notifications.value.length - 1);
      }, 7000);
    }
  },
  { deep: true, immediate: true }
);
</script>

<template>
  <TransitionGroup name="swipe-left" tag="div" class="toast toast-end">
    <div
      v-for="(notification, index) in notifications"
      :key="index"
      class="alert"
      :class="{
        'alert-success': notification.success,
        'alert-error': notification.error,
      }"
    >
      <div class="font-bold">
        <span>{{ notification.messageTitle }}</span>
      </div>
      <div>
        <span>{{ notification.message }}</span>
      </div>
    </div>
  </TransitionGroup>
</template>
