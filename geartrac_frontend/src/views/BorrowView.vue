<script setup>
import { ref } from 'vue'
import { api } from '@/api'

const isVisible = ref(false)

setTimeout(() => {
  isVisible.value = true
}, 200)
</script>

<template>
  <transition name="swipe-up">
    <div v-if="isVisible" class="flex items-center justify-center h-screen text-center flex-col">
      Borrow
    </div>
  </transition>
</template>
