<script setup>
import { ref } from 'vue'
import { authLogIn, authLogOut, authTest } from '@/auth'

const isVisible = ref(false)

setTimeout(() => {
  isVisible.value = true
}, 200)
</script>

<template>
  <transition name="swipe-up">
    <!-- <div v-if="isVisible" class="flex items-center h-screen pt-[8rem] flex-col">
      <Authenticate form-title="Login" />
    </div> -->

    <div class="flex items-center justify-center h-screen pt-[8rem] flex-col">
      <div>
        <button @click="authLogIn">Login Using Google</button>
      </div>
      <div>
        <button @click="authLogOut">Logout Using Google</button>
      </div>
      <div>
        <button @click="authTest">Test Authentication</button>
      </div>
    </div>
  </transition>
 </template>
