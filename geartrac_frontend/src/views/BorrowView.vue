<script setup>
import { ref } from 'vue'
import axios from 'axios'

const isVisible = ref(false)

setTimeout(() => {
  isVisible.value = true
}, 200)

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})
</script>

<template>
  <transition name="swipe-up">
    <div v-if="isVisible" class="flex items-center justify-center h-screen text-center flex-col">
      Borrow
    </div>
  </transition>
</template>
