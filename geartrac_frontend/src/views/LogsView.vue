<script setup>
import { ref, reactive, watch, onMounted } from "vue";
import { api } from "@/api";
import { Button } from "@/components/ui/button";
import Pagination from "@/components/Pagination.vue";
import Notify from "@/components/Notify.vue";

const isVisible = ref(false);
const currentLog = reactive({});

const paginator = reactive({
  logs: [],
  action: null,
  date: null,
  search: null,

  pagesCount: 0,
  currentPage: 1,
  next: null,
  previous: null,
});

const notify = reactive({
  messageTitle: "",
  message: "",
});

watch(
  () => [paginator.action, paginator.date],
  () => {
    isVisible.value = false;
    setTimeout(() => {
      isVisible.value = true;
    }, 200);

    getLogs();
  }
);

watch(
  () => paginator.search,
  () => {
    getLogs();
  }
);

async function getLogs() {
  try {
    if (paginator.action)
      paginator.action = paginator.action.toLowerCase().replace(/ /g, "_");

    const response = await api.get("log/", {
      params: {
        action: paginator.action,
        date: paginator.date,
        page: paginator.currentPage,

        search: paginator.search,
      },
    });

    paginator.logs = response.data.results;
    paginator.pagesCount = response.data.count;
    paginator.next = response.data.next;
    paginator.previous = response.data.previous;
  } catch (error) {
    console.log(error);
  }
}

function getLogColor(logAction) {
  const colors = {
    Use: "bg-emerald-500 text-black hover:bg-emerald-600",
    Unuse: "bg-amber-500 text-black hover:bg-amber-600",
    Borrow: "bg-emerald-500 text-black hover:bg-emerald-600",
    "For Return": "bg-blue-500 text-black hover:bg-blue-600",
    "Slip Confirmed": "bg-teal-500 text-black hover:bg-teal-600",
    "Confirm Return": "bg-cyan-500 text-black hover:bg-cyan-600",
  };

  return colors[logAction] || "";
}

function openLogModal(log) {
  Object.assign(currentLog, log);
  document.querySelector("#logModal").showModal();
}

onMounted(() => {
  getLogs();
  setTimeout(() => {
    isVisible.value = true;
  }, 200);
});
</script>

<template>
  <Notify :notify="notify" />

  <Transition name="swipe-up">
    <div
      v-if="isVisible"
      class="h-screen text-center flex justify-center w-full items-center"
    >
      <div class="flex justify-center gap-2 h-screen items-end w-1/4 flex-col">
        <div>
          <label class="input">
            <svg
              class="h-[1em] opacity-50"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
            >
              <g
                stroke-linejoin="round"
                stroke-linecap="round"
                stroke-width="2.5"
                fill="none"
                stroke="currentColor"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.3-4.3"></path>
              </g>
            </svg>
            <input
              type="search"
              placeholder="Search Gear / Student Name"
              v-model="paginator.search"
            />
          </label>
        </div>

        <div class="flex gap-1">
          <div class="dropdown dropdown-center">
            <Button tabindex="0" role="button" class="btn m-1">{{
              paginator.action ? paginator.action : "Action"
            }}</Button>
            <ul
              tabindex="0"
              class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm rounded-lg"
            >
              <li @click="paginator.action = null"><a>All</a></li>
              <li
                v-for="action in [
                  'Use',
                  'Unuse',
                  'Borrow',
                  'For Return',
                  'Confirm Return',
                  'Slip Confirmed',
                ]"
                :key="action"
                @click="paginator.action = action"
              >
                <a>{{ action }}</a>
              </li>
            </ul>
          </div>
          <!-- <Button @click="paginator.request_user_owner = !paginator.request_user_owner">
          {{ paginator.request_user_owner ? "Used by You" : "Used by Anyone" }}
        </Button>
        <Button @click="cycleAvailability">{{
          paginator.available === null
            ? "All"
            : paginator.available
            ? "Available"
            : "Unavailable"
        }}</Button> -->
        </div>
      </div>

      <div class="flex items-center h-screen text-center w-1/2">
        <div class="container mx-auto px-4 w-fit mt-2">
          <div>
            <Pagination
              v-if="paginator.logs.length"
              :total-items="paginator.pagesCount"
              :current-page="paginator.currentPage"
              :next="paginator.next"
              :previous="paginator.previous"
              class="mb-5"
              @update:current-page="(n) => (paginator.currentPage = n)"
              @update-page="getLogs()"
            />
          </div>

          <div v-if="!paginator.logs.length">
            <h3 class="text-2xl">No logs!</h3>
          </div>
          <div v-for="log in paginator.logs" class="mb-4 p-4 border rounded shadow flex">
            <Button
              class="w-[8rem]"
              :class="getLogColor(log.action)"
              @click="openLogModal(log)"
            >
              {{ log.action }}
            </Button>

            <div class="border-r border-gray-300 mx-4"></div>

            <Button @click="openLogModal(log)">
              {{ log.user }}
            </Button>

            <dialog id="logModal" class="modal">
              <div
                class="modal-box text-left border-2 border-neutral-500 rounded-lg text-white w-fit"
              >
                <h3 class="text-lg font-bold">Action by {{ currentLog.user }}</h3>

                <div class="dropdown dropdown-hover dropdown-start">
                  <div tabindex="0" role="button" class="btn mt-2">View Gear</div>
                  <ul
                    tabindex="0"
                    class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm border"
                    v-for="gear in currentLog.gear"
                  >
                    <li>
                      <a>{{ gear }}</a>
                    </li>
                  </ul>
                </div>

                <div class="mt-5">
                  <h3>Action: {{ currentLog.action }}</h3>
                  <h3>
                    Date:
                    {{
                      new Date(currentLog.timestamp).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })
                    }}
                  </h3>
                </div>

                <div v-if="currentLog.slip_id" class="mt-5 mb-5">
                  <h3>Slip #{{ currentLog.slip_id }}</h3>
                  <h3>Slipped by: {{ currentLog.slipped_by }}</h3>
                </div>

                <div class="modal-action justify-center">
                  <form method="dialog">
                    <button class="btn">Close</button>
                  </form>
                </div>
              </div>
            </dialog>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>
