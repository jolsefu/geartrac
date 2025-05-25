<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { api } from "@/api";
import { userDetails } from "@/auth";
import { Button } from "@/components/ui/button";
import Pagination from "@/components/Pagination.vue";
import Notify from "@/components/Notify.vue";
import "cally";

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
  returnDatePicked: null,
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
    const modal = document.getElementById("borrow-modal");
    modal.showModal();
  }
}

function borrowGear() {
  const returnDate = new Date(paginator.returnDatePicked);
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

function returnDateHandler(datetime) {
  const returnDate = new Date(datetime);
  const currentDate = new Date();
  currentDate.setHours(0, 0, 0, 0);

  if (returnDate <= currentDate) {
    notify.message = "Return date must be a future date.";
    notify.messageTitle = "Error";
    notify.error = true;

    document.querySelector("#borrow-modal").close();

    return (paginator.returnDatePicked = null);
  }

  paginator.returnDatePicked = datetime;
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
    return gear.used || gear.borrowed || isUsedByUser;
  }

  if (unuseToggle.value) {
    return !isUsedByUser;
  }

  if (isUsedByUser) return false;
  return gear.used || gear.borrowed;
}

function openGearModal(gear) {
  Object.assign(currentGear, gear);
  document.querySelector("#gear-modal").showModal();
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
            <Button @click="paginator.request_user_owner = !paginator.request_user_owner">
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
                    :checked="paginator.gearIds.includes(gear.id)"
                  />
                </label>
              </div>

              <div class="border-r border-gray-300 mx-4"></div>

              <h2>
                <Button
                  class="bg-white text-black hover:bg-[#cccccc] hover:text-black"
                  @click="openGearModal(gear)"
                >
                  {{ gear.name }}
                  <span class="text-[#4e4e4e]">
                    {{ gearStatus(gear) }}
                  </span>
                </Button>
              </h2>
            </div>
          </div>
        </div>

        <dialog id="gear-modal" class="modal">
          <div
            class="modal-box text-left border-2 border-neutral-500 rounded-lg text-white w-fit"
          >
            <div>
              <h3 class="text-lg font-bold">
                {{ currentGear.name }}
                {{ currentGear.property_number }}
              </h3>

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
            </div>
            <div class="modal-action justify-start">
              <form method="dialog">
                <button class="btn">Close</button>
              </form>
            </div>
          </div>
        </dialog>
      </div>

      <dialog id="borrow-modal" class="modal">
        <div class="modal-box">
          <div class="font-bold">Borrower's Slip Details</div>
          <div class="modal-action flex justify-center">
            <div>
              <input
                type="date"
                class="input"
                v-model="paginator.returnDatePicked"
                @change="(e) => returnDateHandler(e.target.value)"
              />
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
