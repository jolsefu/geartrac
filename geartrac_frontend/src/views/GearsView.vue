<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { api } from "@/api";
import { userDetails } from "@/auth";
import { Button } from "@/components/ui/button";
import Pagination from "@/components/Pagination.vue";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import Notify from "@/components/Notify.vue";
import "cally";

const returnDatePicked = ref();
const conditionBefore = ref();
const isVisible = ref();
const currentGear = reactive({});
const unuseToggle = ref(false);
const useToggle = ref(false);

const paginator = reactive({
  gears: [],
  gearIds: [],
  available: null,
  request_user_owner: false,
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
  () => [paginator.available, paginator.request_user_owner],
  () => {
    isVisible.value = false;
    setTimeout(() => {
      isVisible.value = true;
    }, 200);

    getGears();
  }
);

watch(
  () => paginator.search,
  () => {
    getGears();
  }
);

async function getGears() {
  try {
    const response = await api.get("gear/", {
      params: {
        page: paginator.currentPage,
        request_user_owner: paginator.request_user_owner,
        available: paginator.available,

        search: paginator.search,
      },
    });

    paginator.gears = response.data.results;
    paginator.pagesCount = response.data.count;
    paginator.next = response.data.next;
    paginator.previous = response.data.previous;
  } catch (error) {
    console.log(error);
  }
}

function cycleAvailability() {
  if (paginator.available === null) {
    paginator.available = true;
  } else if (paginator.available === true) {
    paginator.available = false;
  } else {
    paginator.available = null;
  }
}

function handleCheckboxChange(gear, event) {
  const fullName = `${userDetails.value.first_name} ${userDetails.value.last_name}`;
  const isChecked = event.target.checked;
  const isUsedByUser = gear.used_by === fullName;

  if (isChecked) {
    if (isUsedByUser) unuseToggle.value = true;
    else useToggle.value = true;

    paginator.gearIds.push(gear.id);
  } else {
    paginator.gearIds = paginator.gearIds.filter((gearId) => gearId !== gear.id);

    const noSelectedGears = paginator.gearIds.length === 0;
    if (noSelectedGears) {
      unuseToggle.value = false;
      useToggle.value = false;
    }
  }
}

function useGear() {
  if (!paginator.gearIds.length) {
    notify.message = "Please select a gear.";
    notify.messageTitle = "Error";
    notify.error = true;

    return;
  }

  api
    .post("gear/", {
      action: "use",
      gear_id: paginator.gearIds,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;

      paginator.gearIds = [];

      window.location.reload();
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function unuseGear() {
  api
    .put("gear/", {
      action: "unuse",
      gear_id: paginator.gearIds,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;

      paginator.gearIds = [];

      window.location.reload();
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function handleConditionBefore(e) {
  const condition = e.target.innerText;
  conditionBefore.value = condition;
  document.getElementById("condition-popover").hidePopover();
}

function handleBorrow() {
  if (!paginator.gearIds.length) {
    notify.message = "Please select a gear.";
    notify.messageTitle = "Error";
    notify.error = true;

    return;
  } else {
    const modal = document.getElementById("borrow_modal");
    modal.showModal();
  }
}

function borrowGear() {
  const returnDate = new Date(returnDatePicked.value);
  returnDate.setHours(23, 59, 0);

  api
    .post("gear/", {
      action: "borrow",
      gear_id: paginator.gearIds,
      expected_return_date: returnDate,
      condition_before: conditionBefore.value,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;

      paginator.gearIds = [];

      window.location.reload();
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function gearStatus(gear) {
  const fullName = `${userDetails.value.first_name} ${userDetails.value.last_name}`;
  if (gear.used_by === fullName) return "Used by You";
  else if (gear.borrowed_by === fullName) return "Borrowed by You";
  else if (gear.used || gear.borrowed) return "Not available";
  else return "Available";
}

function gearCheckbox(gear) {
  const fullName = `${userDetails.value.first_name} ${userDetails.value.last_name}`;
  const isUsedByUser = gear.used_by === fullName;

  if (useToggle.value) {
    return isUsedByUser;
  }

  if (unuseToggle.value) {
    return !isUsedByUser;
  }

  if (isUsedByUser) return false;
  return gear.used || gear.borrowed;
}

onMounted(() => {
  getGears();
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
      class="flex items-center justify-center h-screen text-center flex-col"
    >
      <Dialog>
        <div class="flex items-center w-full h-screen justify-center">
          <div class="flex justify-center gap-2 h-screen items-end w-1/4 flex-col">
            <div>
              <input
                type="text"
                placeholder="Enter Gear Name"
                className="input"
                v-model="paginator.search"
              />
            </div>

            <div class="flex gap-1">
              <Button
                @click="paginator.request_user_owner = !paginator.request_user_owner"
              >
                {{ paginator.request_user_owner ? "Used by You" : "Used by Anyone" }}
              </Button>
              <Button @click="cycleAvailability">{{
                paginator.available === null
                  ? "All"
                  : paginator.available
                  ? "Available"
                  : "Unavailable"
              }}</Button>
            </div>
          </div>

          <div class="flex items-center h-screen text-center w-1/2">
            <div class="container mx-auto px-4 w-fit mt-2">
              <div>
                <Pagination
                  v-if="paginator.gears.length"
                  :total-items="paginator.pagesCount"
                  :current-page="paginator.currentPage"
                  :next="paginator.next"
                  :previous="paginator.previous"
                  class="mb-5"
                  @update:current-page="(n) => (paginator.currentPage = n)"
                  @update-page="getGears()"
                />
              </div>
              <div v-if="paginator.gearIds.length" class="flex gap-1 justify-center mb-5">
                <Button
                  class="bg-green-500 text-black hover:bg-green-600"
                  @click="useGear"
                  v-if="useToggle"
                >
                  Use
                </Button>
                <Button
                  class="bg-red-500 text-black hover:bg-red-600"
                  @click="unuseGear"
                  v-if="unuseToggle"
                >
                  Unuse
                </Button>
                <Button
                  class="bg-blue-700 text-black hover:bg-blue-800"
                  @click="handleBorrow"
                >
                  Borrow
                </Button>
              </div>

              <div v-if="!paginator.gears.length">
                <h3 class="text-2xl">No gears!</h3>
              </div>
              <div
                v-for="gear in paginator.gears"
                :key="gear.property_number"
                class="mb-4 p-4 border rounded shadow flex"
              >
                <div class="flex items-center">
                  <label>
                    <input
                      type="checkbox"
                      :value="gear"
                      @change="handleCheckboxChange(gear, $event)"
                      :disabled="gearCheckbox(gear)"
                    />
                  </label>
                </div>

                <div class="border-r border-gray-300 mx-4"></div>

                <h2>
                  <DialogTrigger as-child>
                    <Button
                      class="bg-white text-black hover:bg-[#cccccc] hover:text-black"
                      @click="Object.assign(currentGear, gear)"
                    >
                      {{ gear.name }}
                      <span class="text-[#4e4e4e]">
                        {{ gearStatus(gear) }}
                      </span>
                    </Button>
                  </DialogTrigger>
                </h2>
              </div>
            </div>
          </div>
        </div>

        <DialogContent class="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {{ currentGear.name }}
              {{ currentGear.property_number }}
            </DialogTitle>
            <DialogDescription>
              <div v-if="!currentGear.used && !currentGear.borrowed" class="text-white">
                This gear is available.
              </div>
              <br />
              <div>{{ currentGear.unit_description }}</div>
              <div>Owner: {{ currentGear.owner }}</div>
              <div v-if="currentGear.used_by">Used by: {{ currentGear.used_by }}</div>
              <div v-if="currentGear.borrowed_by">
                Borrowed by: {{ currentGear.borrowed_by }}
              </div>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      <dialog id="borrow_modal" class="modal">
        <div class="modal-box">
          <div class="font-bold">Borrower's Slip Details</div>
          <div class="modal-action">
            <button
              popoverTarget="cally-popover1"
              className="input input-border"
              id="cally1"
              style="anchorname: --cally1"
            >
              {{ returnDatePicked ? returnDatePicked : "Expected Return Date" }}
            </button>
            <div
              popover
              id="cally-popover1"
              className="dropdown bg-base-100 rounded-box shadow-lg"
              style="positionanchor: --cally1"
            >
              <calendar-date
                class="cally"
                :onchange="(e) => (returnDatePicked = e.target.value)"
              >
                <svg
                  aria-label="Previous"
                  className="fill-current size-4"
                  slot="previous"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                >
                  <path d="M15.75 19.5 8.25 12l7.5-7.5"></path>
                </svg>
                <svg
                  aria-label="Next"
                  className="fill-current size-4"
                  slot="next"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                >
                  <path d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
                </svg>
                <calendar-month></calendar-month>
              </calendar-date>
            </div>

            <button
              class="btn btn-info"
              popovertarget="condition-popover"
              style="anchor-name: --anchor-1"
            >
              {{ conditionBefore || "Condition Before" }}
            </button>
            <ul
              class="dropdown menu w-52 rounded-box bg-base-100 shadow-sm"
              popover
              id="condition-popover"
              style="position-anchor: --anchor-1"
            >
              <li><a @click="(e) => handleConditionBefore(e)">Great</a></li>
              <li><a @click="(e) => handleConditionBefore(e)">Good</a></li>
              <li><a @click="(e) => handleConditionBefore(e)">Bad</a></li>
              <li><a @click="(e) => handleConditionBefore(e)">Broken</a></li>
            </ul>

            <div>
              <button class="btn btn-success" @click="borrowGear">Submit</button>
            </div>
            <div>
              <form method="dialog">
                <button class="btn btn-error">Close</button>
              </form>
            </div>
          </div>
        </div>
      </dialog>
    </div>
  </Transition>
</template>
