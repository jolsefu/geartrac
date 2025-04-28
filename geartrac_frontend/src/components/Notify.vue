<script setup>
import { ref, watch } from "vue";
import {
  ToastAction,
  ToastDescription,
  ToastProvider,
  ToastRoot,
  ToastTitle,
  ToastViewport,
} from "reka-ui";

const props = defineProps({
  notify: { type: Object, required: true },
});

const open = ref(true);

let timeoutId;

function clearNotify() {
  if (timeoutId) {
    clearTimeout(timeoutId);
    timeoutId = null;
  }

  open.value = false;
  props.notify.message = "";
  props.notify.messageTitle = "";
  props.notify.error = false;
  props.notify.message = false;
  props.notify.success = false;
}

watch(
  props.notify,
  (newNotify) => {
    if (newNotify.message && newNotify.messageTitle && !open.value) {
      open.value = true;

      timeoutId = setTimeout(() => {
        open.value = false;
      }, 7000);
    }
  },
  { deep: true, immediate: true }
);
</script>

<template>
  <ToastProvider>
    <ToastRoot
      :open="open"
      :class="{
        'text-red-600': notify.error,
        'text-green-600': notify.success,
        'text-white': notify.default,
      }"
      class="bg-[var(--tertiary-color)] rounded-lg shadow-sm border p-[15px] grid [grid-template-areas:_'title_action'_'description_action'] grid-cols-[auto_max-content] gap-x-[15px] items-center"
    >
      <ToastTitle class="[grid-area:_title] mb-[5px] font-medium text-slate12 text-sm">
        {{ notify.messageTitle }}
      </ToastTitle>
      <ToastDescription as-child>
        {{ notify.message }}
      </ToastDescription>
      <ToastAction class="[grid-area:_action]" as-child alt-text="Goto schedule to undo">
        <button
          @click="clearNotify"
          class="inline-flex items-center justify-center rounded-md font-medium text-xs px-[10px] leading-[25px] h-[25px] bg-green2 text-green11 shadow-[inset_0_0_0_1px] shadow-green7 hover:shadow-[inset_0_0_0_1px] hover:shadow-green8 focus:shadow-[0_0_0_2px] focus:shadow-green8"
        >
          Close
        </button>
      </ToastAction>
    </ToastRoot>
    <ToastViewport
      class="[--viewport-padding:_25px] fixed bottom-0 right-0 flex flex-col p-[var(--viewport-padding)] gap-[10px] w-[390px] max-w-[100vw] m-0 list-none z-[2147483647] outline-none"
    />
  </ToastProvider>
</template>

<style scoped></style>
