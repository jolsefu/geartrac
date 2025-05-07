<script setup>
import { ref, reactive, onMounted } from "vue";
import { api } from "@/api";
import { userDetails } from "@/auth";
import { Button } from "@/components/ui/button";
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
const gears = ref();
const gearIds = ref([]);
const currentGear = ref({});
const notify = reactive({
  messageTitle: "",
  message: "",
});

setTimeout(() => {
  isVisible.value = true;
}, 200);

async function getGears() {
  try {
    const response = await api.get("gear/");
    gears.value = response.data;
  } catch (error) {
    console.log(error);
  }
}

function handleCheckboxChange(id, event) {
  if (event.target.checked) {
    gearIds.value.push(id);
  } else {
    gearIds.value = gearIds.value.filter((gearId) => gearId !== id);
  }
}

function useGear() {
  if (!gearIds.value.length) {
    notify.message = "Please select a gear.";
    notify.messageTitle = "Error";
    notify.error = true;

    return;
  }

  api
    .post("gear/", {
      action: "use",
      gear_id: gearIds.value,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;

      gearIds.value = [];

      window.location.reload();
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function unuseGear(gear_id) {
  api
    .put("gear/", {
      action: "unuse",
      gear_id: gear_id,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;

      getGears();
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
  if (!gearIds.value.length) {
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
      gear_id: gearIds.value,
      expected_return_date: returnDate,
      condition_before: conditionBefore.value,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;

      gearIds.value = [];

      window.location.reload();
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

onMounted(() => {
  getGears();
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
        <div class="container mx-auto px-4 max-w-min mt-16">
          <div class="mb-5 flex justify-center gap-1">
            <Button class="bg-green-500 text-black hover:bg-green-600" @click="useGear">
              Use
            </Button>
            <Button
              class="bg-blue-700 text-black hover:bg-blue-800"
              @click="handleBorrow"
            >
              Borrow
            </Button>
          </div>
          <div
            v-for="gear in gears"
            :key="gear.property_number"
            class="mb-4 p-4 border rounded shadow flex"
          >
            <div class="flex items-center">
              <label>
                <input
                  type="checkbox"
                  :value="gear"
                  @change="handleCheckboxChange(gear.id, $event)"
                  :disabled="gear.used || gear.borrowed"
                />
              </label>
            </div>

            <div class="border-r border-gray-300 mx-4"></div>

            <h2>
              <DialogTrigger as-child>
                <Button
                  class="bg-white text-black hover:bg-[#cccccc] hover:text-black"
                  @click="currentGear.value = gear"
                >
                  {{ gear.name }}
                  <span class="text-[#4e4e4e]">
                    {{ gear.used || gear.borrowed ? "Not available" : "Available" }}
                  </span>
                </Button>
              </DialogTrigger>
            </h2>
          </div>
        </div>

        <DialogContent class="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {{ currentGear.value.name }}
              {{ currentGear.value.property_number }}
            </DialogTitle>
            <DialogDescription>
              <div
                v-if="!currentGear.value.used && !currentGear.value.borrowed"
                class="text-white"
              >
                This gear is available.
              </div>
              <br />
              <div>{{ currentGear.value.unit_description }}</div>
              <div>Owner: {{ currentGear.value.owner }}</div>
              <div v-if="currentGear.value.used_by">
                Used by: {{ currentGear.value.used_by }}
              </div>
              <div v-if="currentGear.value.borrowed_by">
                Borrowed by: {{ currentGear.value.borrowed_by }}
              </div>
            </DialogDescription>

            <div v-if="currentGear.value.used_by">
              <Button
                id="unusedButton"
                class="bg-red-500 text-black hover:bg-red-600 w-fit mt-4"
                v-if="
                  !currentGear.value.used_by.localeCompare(
                    `${userDetails.first_name} ${userDetails.last_name}`
                  )
                "
                @click="unuseGear(currentGear.value.id)"
              >
                Mark as unused
              </Button>
            </div>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      <dialog id="borrow_modal" class="modal">
        <div class="modal-box">
          <div class="font-bold">Expected Return Date</div>
          <div class="modal-action">
            <button
              popoverTarget="cally-popover1"
              className="input input-border"
              id="cally1"
              style="anchorname: --cally1"
            >
              {{ returnDatePicked ? returnDatePicked : "Pick A Date" }}
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
