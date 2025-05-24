<script setup>
import { ref, reactive, onMounted } from "vue";
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

async function getLogs() {
  try {
    const response = await api.get("log/", {
      params: {
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
          <input
            type="text"
            placeholder="Enter Log User or Gear"
            className="input"
            v-model="paginator.search"
          />
        </div>

        <div class="flex gap-1">
          <Button>Action</Button>
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
              :class="getLogColor(log.action)"
              @click="
                currentLog = log;
                logModal?.showModal();
              "
            >
              {{ log.action }}
            </Button>

            <div class="border-r border-gray-300 mx-4"></div>

            <Button @click="openLogModal(log)">
              {{ log.user }}
            </Button>

            <dialog id="logModal" class="modal modal-bottom sm:modal-middle">
              <div
                class="modal-box text-left border-2 border-white rounded-lg text-white"
              >
                <h3 class="text-lg font-bold">Action by {{ currentLog.user }}</h3>

                <details class="dropdown mt-5">
                  <summary class="btn">View Gear</summary>
                  <ul
                    class="menu dropdown-content bg-base-100 rounded-box z-1 w-52 shadow-sm"
                  >
                    <li v-for="gear in currentLog.gear">
                      {{ gear }}
                    </li>
                  </ul>
                </details>

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
                  <h3>#{{ currentLog.slip_id }}</h3>
                  <h3>Slipped by: {{ currentLog.slipped_by }}</h3>
                </div>

                <div class="modal-action">
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
