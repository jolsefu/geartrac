<script setup>
import { ref, reactive, onMounted, watch } from "vue";
import { api } from "@/api";
import { Button } from "@/components/ui/button";
import { userPermissionLevel, userDetails } from "@/auth";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import Notify from "@/components/Notify.vue";
import Pagination from "@/components/Pagination.vue";

const isVisible = ref(false);
const currentSlip = ref(false);
const conditionAfter = ref();

const paginator = reactive({
  slips: [],
  archived: false,
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
  () => paginator.archived,
  () => {
    isVisible.value = false;
    setTimeout(() => {
      isVisible.value = true;
    }, 200);

    getSlips();
  }
);

watch(
  () => paginator.search,
  () => {
    getSlips();
  }
);

async function getSlips() {
  try {
    const response = await api.get("slip/", {
      params: {
        paginator: paginator.currentPage,
        archived: paginator.archived,

        search: paginator.search,
      },
    });

    paginator.slips = response.data.results;
    paginator.pagesCount = response.data.count;
    paginator.next = response.data.next;
    paginator.previous = response.data.previous;
  } catch (error) {
    console.log(error);
  }
}

function acceptSlip(slip_id) {
  api
    .put("slip/", {
      action: "accept",
      slip_id: slip_id,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function declineSlip(slip_id) {
  api
    .put("slip/", {
      action: "decline",
      slip_id: slip_id,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function returnSlip(slip_id) {
  api
    .put("slip/", {
      action: "return",
      slip_id: slip_id,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function acknowledgeReturn(slip_id) {
  api
    .put("slip/", {
      action: "acknowledge_return",
      slip_id: slip_id,
      condition_after: conditionAfter.value,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
      notify.success = true;
    })
    .catch((error) => {
      notify.message = error.response.data.error;
      notify.messageTitle = error.response.status === 200 ? "Success" : "Error";
      notify.error = true;
    });
}

function handleConditionAfter(e) {
  const condition = e.target.innerText;
  conditionAfter.value = condition;
  document.getElementById("condition-popover").hidePopover();
}

onMounted(() => {
  getSlips();
  setTimeout(() => {
    isVisible.value = true;
  }, 200);
});
</script>

<template>
  <Notify :notify="notify" />

  <Transition name="swipe-up">
    <div v-if="isVisible" class="flex justify-center">
      <div
        class="flex justify-center items-end h-screen text-center w-1/4 text-2xl flex-col gap-1"
      >
        <div>
          <input
            type="text"
            placeholder="Enter Slip Name"
            className="input"
            v-model="paginator.search"
          />
        </div>
        <div>
          <Button @click="paginator.archived = !paginator.archived">{{
            paginator.archived ? "Archived Slips" : "Active Slips"
          }}</Button>
        </div>
      </div>

      <div
        v-if="!paginator.slips.length"
        class="flex justify-center items-center h-screen text-center w-1/2 text-2xl"
      >
        <h3 class="text-2xl">
          {{ paginator.archived ? "No Archived Slips!" : "No Slips!" }}
        </h3>
      </div>

      <div
        v-if="paginator.slips.length"
        class="flex items-center h-screen text-center w-1/2"
      >
        <Dialog>
          <div class="container mx-auto px-4 w-fit mt-2">
            <Pagination
              :total-items="paginator.pagesCount"
              :current-page="paginator.currentPage"
              :next="paginator.next"
              :previous="paginator.previous"
              class="mb-5"
              @update:current-page="(n) => (paginator.currentPage = n)"
              @update-page="getSlips()"
            />

            <div
              v-for="slip in paginator.slips"
              class="mb-4 p-4 border rounded shadow flex"
            >
              <div class="flex justify-center items-center flex-col">
                <div>
                  {{ slip.for_return ? "(For Return)" : "" }}
                </div>
                <div>Slip #{{ slip.custom_id }}</div>
              </div>
              <div class="border-l h-12 mx-4"></div>
              <div class="flex justify-center items-center">
                <h2>
                  <DialogTrigger as-child>
                    <Button
                      class="bg-white text-black hover:bg-[#cccccc] hover:text-black"
                      @click="currentSlip = slip"
                    >
                      View More
                    </Button>
                  </DialogTrigger>
                </h2>
              </div>
            </div>
          </div>

          <DialogContent class="sm:max-w-[600px] flex">
            <DialogHeader class="flex flex-col justify-center items-center">
              <div class="flex mb-3">
                <DialogTitle> {{ currentSlip.slipped_by }} </DialogTitle>
              </div>

              <DialogDescription>
                <div class="capitalize">
                  Condition Before: {{ currentSlip.condition_before }}
                </div>
                <div v-if="paginator.archived" class="capitalize">
                  Condition After: {{ currentSlip.condition_after }}
                </div>
                <div>
                  Borrowed Date:
                  {{ new Date(currentSlip.borrowed_date).toLocaleString() }}
                </div>
                <div>
                  Expected Return Date:
                  {{ new Date(currentSlip.expected_return_date).toLocaleString() }}
                </div>
                <div v-if="paginator.archived">
                  Return Date: {{ new Date(currentSlip.return_date).toLocaleString() }}
                </div>
              </DialogDescription>

              <div class="mt-5">
                <div class="flex items-center">
                  <details class="dropdown">
                    <summary class="btn m-1">View Borrowed Gear</summary>
                    <ul
                      class="menu dropdown-content bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm"
                    >
                      <li v-for="gear in currentSlip.gear_borrowed">
                        {{ gear }}
                      </li>
                    </ul>
                  </details>

                  <div v-if="!paginator.archived">
                    <button
                      v-if="userPermissionLevel >= 2 && !currentSlip.for_return"
                      class="btn btn-success"
                      @click="acceptSlip(currentSlip.custom_id)"
                    >
                      Accept
                    </button>
                    <button
                      v-if="userPermissionLevel >= 2 && !currentSlip.for_return"
                      class="btn btn-warning"
                      @click="declineSlip(currentSlip.custom_id)"
                    >
                      Decline
                    </button>
                  </div>
                </div>
                <button
                  v-if="
                    currentSlip.editor_in_chief_signature &&
                    currentSlip.slipped_by ===
                      `${userDetails.first_name} ${userDetails.last_name}`
                  "
                  class="btn btn-info"
                  @click="returnSlip(currentSlip.custom_id)"
                >
                  Return
                </button>
                <button
                  v-if="userPermissionLevel >= 2 && currentSlip.for_return"
                  class="btn btn-info"
                  @click="acknowledgeReturn(currentSlip.custom_id)"
                >
                  Accept Return
                </button>

                <button
                  class="btn btn-info"
                  v-if="currentSlip.for_return"
                  popovertarget="condition-popover"
                  style="anchor-name: --anchor-1"
                >
                  {{ conditionAfter || "Condition After" }}
                </button>
                <ul
                  class="dropdown menu w-52 rounded-box bg-base-100 shadow-sm"
                  popover
                  id="condition-popover"
                  style="position-anchor: --anchor-1"
                >
                  <li><a @click="(e) => handleConditionAfter(e)">Great</a></li>
                  <li><a @click="(e) => handleConditionAfter(e)">Good</a></li>
                  <li><a @click="(e) => handleConditionAfter(e)">Bad</a></li>
                  <li><a @click="(e) => handleConditionAfter(e)">Broken</a></li>
                </ul>
              </div>
            </DialogHeader>

            <div class="ml-5">
              <ul class="timeline timeline-vertical timeline-compact">
                <li>
                  <div class="timeline-start timeline-box">Section Editor</div>
                  <div class="timeline-middle">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      class="h-5 w-5"
                      :class="{ 'text-success': currentSlip.section_editor_signature }"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                  <hr :class="{ 'bg-success': currentSlip.section_editor_signature }" />
                </li>
                <li>
                  <hr :class="{ 'bg-success': currentSlip.section_editor_signature }" />
                  <div class="timeline-start timeline-box">Circulations Manager</div>
                  <div class="timeline-middle">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      class="h-5 w-5"
                      :class="{
                        'text-success': currentSlip.circulations_manager_signature,
                      }"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                  <hr
                    :class="{ 'bg-success': currentSlip.circulations_manager_signature }"
                  />
                </li>
                <li>
                  <hr
                    :class="{ 'bg-success': currentSlip.circulations_manager_signature }"
                  />
                  <div class="timeline-start timeline-box">Managing Editor</div>
                  <div class="timeline-middle">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      class="h-5 w-5"
                      :class="{
                        'text-success': currentSlip.managing_editor_signature,
                      }"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                  <hr
                    :class="{
                      'bg-success': currentSlip.managing_editor_signature,
                    }"
                  />
                </li>
                <li>
                  <hr
                    :class="{
                      'bg-success': currentSlip.managing_editor_signature,
                    }"
                  />
                  <div class="timeline-start timeline-box">Editor-in-Chief</div>
                  <div class="timeline-middle">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      class="h-5 w-5"
                      :class="{
                        'text-success': currentSlip.editor_in_chief_signature,
                      }"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </div>
                </li>
              </ul>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  </Transition>
</template>
