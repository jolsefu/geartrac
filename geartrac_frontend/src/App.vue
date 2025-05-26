<script setup>
import { ref, reactive } from "vue";
import { api } from "./api";
import { isAuthenticated, userPermissionLevel } from "@/auth";

const isMenuOpen = ref(false);
const currentNotification = reactive({});

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
};

const show = ref(false);

setTimeout(() => {
  show.value = true;
}, 500);

// Notifications

import { onMounted, onBeforeUnmount } from "vue";

const notifications = ref([]);

let socket;

onMounted(() => {
  socket = new WebSocket("ws://localhost:8000/ws/notifications/");

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type == "initial_notifications") {
      data.notifications.forEach((notification) => {
        notifications.value.push(notification);
      });
    } else if (data.type == "notification_update") {
      const existingIndex = notifications.value.findIndex(
        (notification) => notification.id === data.notification.id
      );
      if (existingIndex !== -1) {
        notifications.value[existingIndex] = data.notification;
      } else {
        notifications.value.unshift(data.notification);
      }
    }
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected");
  };
});

function openNotificationModal(notification) {
  Object.assign(currentNotification, notification);
  document.querySelector("#notification-modal").showModal();

  api.post("notification/", {
    action: "mark_as_read",
    notification_ids: [notification.id],
  });
}

function markAllAsRead() {
  api.post("notification/", {
    action: "mark_all_as_read",
  });
}

onBeforeUnmount(() => {
  if (socket) {
    socket.close();
  }
});
</script>

<template>
  <Transition name="swipe-down">
    <nav v-if="show" class="bg-[#181818] fixed w-full z-20 top-0 start-0 border-b">
      <div class="max-w-screen-xl flex items-center justify-between mx-auto p-4">
        <a href="/" class="text-2xl font-semibold text-white"> GearTRAC </a>

        <div
          class="hidden md:flex absolute left-1/2 transform -translate-x-1/2 whitespace-nowrap"
        >
          <ul class="flex space-x-8 text-lg">
            <li>
              <RouterLink
                to="/"
                class="text-white hover:-translate-y-1 transition duration-300 ease-in-out"
              >
                Home
              </RouterLink>
            </li>
            <li>
              <RouterLink
                to="/about"
                class="text-white hover:-translate-y-1 transition duration-300 ease-in-out"
              >
                About
              </RouterLink>
            </li>
            <li v-if="isAuthenticated">
              <RouterLink
                to="/gears"
                class="text-white hover:-translate-y-1 transition duration-300 ease-in-out"
              >
                Gears
              </RouterLink>
            </li>
            <li v-if="isAuthenticated">
              <RouterLink
                to="/slips"
                class="text-white hover:-translate-y-1 transition duration-300 ease-in-out"
              >
                Slips
              </RouterLink>
            </li>
            <li v-if="isAuthenticated && userPermissionLevel >= 2">
              <RouterLink
                to="/logs"
                class="text-white hover:-translate-y-1 transition duration-300 ease-in-out"
              >
                Logs
              </RouterLink>
            </li>
          </ul>
        </div>

        <div class="flex items-center space-x-4 ml-auto">
          <RouterLink
            v-if="!isAuthenticated"
            to="/login"
            class="hidden md:block text-white px-4 py-2 bg-[#3b3b3b] hover:bg-[#505050] rounded-lg transition duration-300"
          >
            Log In
          </RouterLink>
          <div v-if="isAuthenticated" class="dropdown dropdown-center">
            <div
              tabindex="0"
              role="button"
              class="btn m-1 flex justify-center items-center rounded-lg"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#FFFFFF"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"
                ></path>
              </svg>
            </div>
            <ul
              tabindex="0"
              class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm rounded-lg"
            >
              <li
                v-for="notification in notifications"
                class="text-white flex flex-col"
                @click="openNotificationModal(notification)"
              >
                <div class="rounded-lg">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="8"
                    height="8"
                    fill="gray"
                    viewBox="0 0 24 24"
                    class="inline-block mr-2"
                    v-if="!notification.read"
                  >
                    <circle cx="12" cy="12" r="8" />
                  </svg>
                  {{
                    notification.message.length > 10
                      ? notification.message.slice(0, 10) + "..."
                      : notification.message
                  }}
                  <br />
                  <span class="text-gray-500">
                    {{
                      (() => {
                        const now = new Date();
                        const notificationTime = new Date(notification.timestamp);
                        const elapsed = Math.floor((now - notificationTime) / 1000);

                        if (elapsed < 60) return "Now";
                        if (elapsed < 3600) return `${Math.floor(elapsed / 60)}m`;
                        if (elapsed < 86400) return `${Math.floor(elapsed / 3600)}h`;
                        return `${Math.floor(elapsed / 86400)}d`;
                      })()
                    }}
                  </span>
                </div>
              </li>
              <div
                class="text-blue-500 mt-2 flex justify-center hover:cursor-pointer"
                @click="markAllAsRead"
              >
                Mark all as read
              </div>
            </ul>
          </div>
          <RouterLink
            v-if="isAuthenticated"
            to="/login"
            class="hidden md:block text-white px-4 py-2 bg-[#3b3b3b] hover:bg-[#505050] rounded-lg transition duration-300"
          >
            Profile
          </RouterLink>

          <button
            @click="toggleMenu"
            class="md:hidden p-2 w-10 h-10 justify-center text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-600"
          >
            <span class="sr-only">Open main menu</span>
            <svg
              class="w-6 h-6"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 17 14"
            >
              <path
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M1 1h15M1 7h15M1 13h15"
              />
            </svg>
          </button>
        </div>

        <!-- Mobile Menu -->
        <transition name="menu-slide">
          <div
            v-if="isMenuOpen"
            class="border-b absolute top-16 left-0 w-full bg-[#181818] md:hidden"
          >
            <ul class="items-center text-center flex flex-col p-4 text-lg">
              <li>
                <RouterLink
                  to="/"
                  class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300"
                >
                  Home
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  to="/about"
                  class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300"
                >
                  About
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  v-if="!isAuthenticated"
                  to="/login"
                  class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300"
                >
                  Log In
                </RouterLink>
                <RouterLink
                  v-else
                  to="/login"
                  class="block py-2 px-3 text-white hover:bg-[#3b3b3b] rounded-sm transition duration-300"
                >
                  Profile
                </RouterLink>
              </li>
            </ul>
          </div>
        </transition>
      </div>
    </nav>
  </Transition>

  <dialog id="notification-modal" class="modal">
    <div
      class="modal-box text-left border-2 border-neutral-500 rounded-lg text-white max-w-1/2"
    >
      <div>
        <h3 class="text-lg font-bold">
          {{ currentNotification.message }}
        </h3>

        <div>
          <span class="text-gray-500">
            {{
              (() => {
                const now = new Date();
                const notificationTime = new Date(currentNotification.timestamp);
                const elapsed = Math.floor((now - notificationTime) / 1000);

                if (elapsed < 60) return "Now";
                if (elapsed < 3600) return `${Math.floor(elapsed / 60)}m`;
                if (elapsed < 86400) return `${Math.floor(elapsed / 3600)}h`;
                return `${Math.floor(elapsed / 86400)}d`;
              })()
            }}
          </span>
        </div>
      </div>
      <div class="modal-action justify-start">
        <form method="dialog">
          <button class="btn">Close</button>
        </form>
      </div>
    </div>
  </dialog>

  <RouterView />
</template>

<style scoped>
.menu-slide-enter-active,
.menu-slide-leave-active {
  transition: opacity 0.3s ease-in-out;
}
.menu-slide-enter-from,
.menu-slide-leave-to {
  opacity: 0;
}
</style>

<style>
.swipe-down-enter-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}
.swipe-down-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.swipe-down-leave-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-down-leave-from {
  opacity: 1;
  transform: translateY(0);
}
.swipe-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
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
.swipe-up-leave-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-up-leave-from {
  opacity: 1;
  transform: translateY(0);
}
.swipe-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.swipe-right-enter-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-right-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
.swipe-right-enter-to {
  opacity: 1;
  transform: translateX(0);
}
.swipe-right-leave-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-right-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.swipe-right-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.swipe-left-enter-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-left-enter-from {
  opacity: 0;
  transform: translateX(10px);
}
.swipe-left-enter-to {
  opacity: 1;
  transform: translateX(0);
}
.swipe-left-leave-active {
  transition: opacity 1s ease-in-out, transform 1s ease-in-out;
}
.swipe-left-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.swipe-left-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
</style>
