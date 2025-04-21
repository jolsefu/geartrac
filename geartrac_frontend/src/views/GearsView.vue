<script setup>
import { ref } from 'vue'
import axios from 'axios'

const isVisible = ref(false)

setTimeout(() => {
  isVisible.value = true
}, 200)

const gears = ref([])

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

const getGears = async () => {
  try {
    const response = await api.get('gear/')
    gears.value = response.data
  } catch (error) {
    console.log(error)
  }
}

getGears()

</script>

<template>
  <transition name="swipe-up">
    <div v-if="isVisible" class="flex items-center justify-center h-screen text-center flex-col">
      <div class="container mx-auto px-4 max-w-4xl mt-16">
        <div v-for="gear in gears" :key="gear.property_number" class="mb-4 p-4 border rounded shadow">
          <h2 class="text-xl font-bold">{{ gear.name }}</h2>
          <p class="text-gray-600">{{ gear.unit_description }}</p>
          <p><strong>Property Number:</strong> {{ gear.property_number }}</p>
          <p><strong>Owner:</strong> {{ gear.owner }}</p>
          <p><strong>Used:</strong> {{ gear.used ? 'Yes' : 'No' }}</p>
          <p><strong>Borrowed:</strong> {{ gear.borrowed ? 'Yes' : 'No' }}</p>
        </div>
      </div>
    </div>
  </transition>

</template>
