<script setup>
import { ref, reactive, onMounted } from "vue";
import { api } from "@/api";
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

const isVisible = ref(false);
const slips = ref([]);
const currentSlip = ref(false);

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

onMounted(() => {
  getSlips();
});
</script>

<template>
  <Transition name="swipe-up">
    <div
      v-if="isVisible"
      class="flex items-center justify-center h-screen text-center flex-col"
    >
      <Dialog>
        <div class="container mx-auto px-4 w-fit mt-16">
          <div v-for="slip in slips" class="mb-4 p-4 border rounded shadow flex flex-col">
            <div>{{ new Date(slip.borrowed_date).toLocaleString() }}</div>

            <h2>
              <DialogTrigger as-child>
                <Button
                  class="bg-white text-black hover:bg-[#cccccc] hover:text-black"
                  @click="currentSlip = slip"
                >
                  {{ slip.slipped_by }}
                </Button>
              </DialogTrigger>
            </h2>
          </div>
        </div>

        <DialogContent class="sm:max-w-[600px] flex">
          <DialogHeader class="flex flex-col justify-center items-center">
            <div class="flex justify-center">
              <DialogTitle> Borrower's Slip by {{ currentSlip.slipped_by }} </DialogTitle>
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

            <div class="justify-center flex">
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
