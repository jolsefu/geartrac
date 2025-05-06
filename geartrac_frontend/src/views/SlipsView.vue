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

        <DialogContent class="sm:max-w-[425px]">
          <DialogHeader class="flex">
            <div class="flex justify-center">
              <DialogTitle> Borrower's Slip by {{ currentSlip.slipped_by }} </DialogTitle>
            </div>

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
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  </Transition>
</template>
