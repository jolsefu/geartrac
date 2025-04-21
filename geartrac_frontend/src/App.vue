<script setup>
import { ref } from 'vue'
import { isAuthenticated } from './auth'

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}
</script>

<template>
  <nav class="bg-[#181818] fixed w-full z-20 top-0 start-0 border-b">
    <div class="max-w-screen-xl flex items-center justify-between mx-auto p-4">
      <a href="/" class="text-2xl font-semibold text-white">
        GearTRAC
      </a>

      <div class="hidden md:flex absolute left-1/2 transform -translate-x-1/2 whitespace-nowrap">
        <ul class="flex space-x-8 text-lg">
          <li>
            <RouterLink to="/" class="text-white hover:-translate-y-1 transition duration-300 ease-in-out">
              Home
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/about" class="text-white hover:-translate-y-1 transition duration-300 ease-in-out">
              About
            </RouterLink>
          </li>
          <li v-if="isAuthenticated">
            <RouterLink to="/gears" class="text-white hover:-translate-y-1 transition duration-300 ease-in-out">
              Gears
            </RouterLink>
          </li>
          <li v-if="isAuthenticated">
            <RouterLink to="/borrow" class="text-white hover:-translate-y-1 transition duration-300 ease-in-out">
              Borrow
            </RouterLink>
          </li>
        </ul>
      </div>

      <div class="flex items-center space-x-4 ml-auto">
        <RouterLink v-if="!isAuthenticated" to="/login" class="hidden md:block text-white px-4 py-2 bg-[#3b3b3b] hover:bg-[#505050] rounded-lg transition duration-300">
          Log In
        </RouterLink>
        <RouterLink v-else to="/login" class="hidden md:block text-white px-4 py-2 bg-[#3b3b3b] hover:bg-[#505050] rounded-lg transition duration-300">
          Profile
        </RouterLink>

        <button
          @click="toggleMenu"
          class="md:hidden p-2 w-10 h-10 justify-center text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-600">
          <span class="sr-only">Open main menu</span>
          <svg class="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 17 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 1h15M1 7h15M1 13h15"/>
          </svg>
        </button>
      </div>

      <!-- Mobile Menu -->
      <transition name="menu-slide">
        <div v-if="isMenuOpen" class="border-b absolute top-16 left-0 w-full bg-[#181818] md:hidden">
          <ul class="items-center text-center flex flex-col p-4 text-lg">
            <li>
              <RouterLink to="/" class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300">
                Home
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/about" class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300">
                About
              </RouterLink>
            </li>
            <li>
              <RouterLink v-if="!isAuthenticated" to="/login" class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300">
                Log In
              </RouterLink>
              <RouterLink v-else to="/login" class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300">
                Profile
              </RouterLink>
            </li>
          </ul>
        </div>
      </transition>
    </div>
  </nav>


  <RouterView />
</template>

<style scoped>
.menu-slide-enter-active, .menu-slide-leave-active {
  transition: opacity 0.3s ease-in-out;
}
.menu-slide-enter-from, .menu-slide-leave-to {
  opacity: 0;
}
</style>


<style>
.swipe-down-enter-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-down-enter-from {
  opacity: 0; transform: translateY(-10px);
}
.swipe-down-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.swipe-up-enter-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.swipe-up-enter-to {
  opacity: 1;
  transform: translateY(0);
}
</style>
