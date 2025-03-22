<script setup>
const props = defineProps({
  formTitle: String,
})
</script>

<template>
  <div class="w-full max-w-sm md:bg-[var(--tertiary-color)] md:shadow-xl sm:max-w-md max-auto lg:max-w-xl p-6 space-y-8 sm:p-8 rounded-lg bg-[var(--primary-color)]">
    <h2 class="text-center text-2xl font-bold text-gray-900 dark:text-white">
      {{ formTitle }} to GearTRAC
    </h2>
    <form class="mt-8 space-y-6" action="#">
      <div>
        <label for="email" class="block mb-2 text-sm font-medium text-white">Email</label>
        <input type="email" name="email" id="email" class="text-sm rounded-lg block w-full p-2.5 bg-[#3b3b3b]" placeholder="name@company.com" required />
      </div>
      <div>
        <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Your password</label>
        <input type="password" name="password" id="password" class="text-sm rounded-lg block w-full p-2.5 bg-[#3b3b3b]" placeholder="••••••••" required />
      </div>
      <!-- <div class="flex items-start">
        <div class="flex items-center h-5">
            <input id="remember" aria-describedby="remember" name="remember" type="checkbox" class="w-4 h-4 border-gray-300 rounded-sm bg-gray-50 focus:ring-3 focus:ring-blue-300 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600" required />
        </div>
        <div class="ms-3 text-sm">
        <label for="remember" class="text-white font-medium">Remember this device</label>
        </div>
        <a href="#" class="text-white ms-auto text-sm font-medium hover:underline">Lost Password?</a>
      </div> -->
      <div class="text-center space-y-3">
        <button type="submit" class="px-5 py-3 font-medium text-center text-white bg-[var(--secondary-color)] rounded-lg hover:bg-[var(--hover-color)] transition duration-300 w-auto">{{ formTitle }}</button>
        <div v-if="formTitle == 'Login'" class="text-sm font-medium">
          Not registered yet? <RouterLink to="signup"><a class="text-blue-600 hover:underline cursor-pointer">Create account</a></RouterLink>
        </div>
      </div>
    </form>
  </div>
</template>

<style scoped>
</style>
