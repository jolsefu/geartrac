<script setup>
import { ref, reactive, onMounted } from "vue";
import { api } from "@/api";
import { Button } from "@/components/ui/button";
import { userPermissionLevel } from "@/auth";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import Notify from "@/components/Notify.vue";

const isVisible = ref(false);
const slips = ref([]);
const currentSlip = ref(false);
const conditionAfter = ref();
const notify = reactive({
  messageTitle: "",
  message: "",
});

setTimeout(() => {
  isVisible.value = true;
}, 200);

async function getSlips() {
  try {
    const response = await api.get("slip/");
    slips.value = response.data;
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
});
</script>

<template>
  <Notify :notify="notify" />

  <Transition name="swipe-up">
    <div
      v-if="isVisible"
      class="flex items-center justify-center h-screen text-center flex-col"
    >
      <h3 class="text-2xl" v-if="!slips.length">No slips!</h3>
      <Dialog>
        <div class="container mx-auto px-4 w-fit mt-2">
          <div v-for="slip in slips" class="mb-4 p-4 border rounded shadow flex">
            <div class="flex justify-center items-center flex-col">
              <div>
                {{ slip.for_return ? "(For Return)" : "" }}
              </div>
              <div>
                Slip #{{ new Date().getFullYear() }}-{{
                  slip.id.toString().padStart(3, "0")
                }}
              </div>
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
              <div>Condition Before: {{ currentSlip.condition_before }}</div>
              <div>
                Borrowed Date: {{ new Date(currentSlip.borrowed_date).toLocaleString() }}
              </div>
              <div>
                Expected Return Date:
                {{ new Date(currentSlip.expected_return_date).toLocaleString() }}
              </div>
            </DialogDescription>

            <div class="mt-5">
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

              <button
                v-if="userPermissionLevel >= 2 && !currentSlip.for_return"
                class="btn btn-success"
                @click="acceptSlip(currentSlip.id)"
              >
                Accept Slip
              </button>
              <button
                v-if="currentSlip.editor_in_chief_signature && userPermissionLevel == 1"
                class="btn btn-info"
                @click="returnSlip(currentSlip.id)"
              >
                Return
              </button>
              <button
                v-if="userPermissionLevel >= 2 && currentSlip.for_return"
                class="btn btn-info"
                @click="acknowledgeReturn(currentSlip.id)"
              >
                Accept Return
              </button>

              <button
                class="btn btn-info"
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
  </Transition>
</template>
