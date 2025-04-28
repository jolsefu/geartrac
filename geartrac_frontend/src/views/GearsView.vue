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

const getGears = async () => {
  try {
    const response = await api.get("gear/");
    gears.value = response.data;
  } catch (error) {
    console.log(error);
  }
};

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
    notify.error = false;
  }

  api
    .post("gear/", {
      action: "use",
      gear_id: gearIds.value,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
    });
}

function borrowGear() {
  api
    .post("gear/", {
      action: "borrow",
      gear_id: gearIds.value,
    })
    .then((response) => {
      notify.message = response.data.message;
      notify.messageTitle = response.status === 200 ? "Success" : "Error";
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
            <Button class="bg-blue-700 text-black hover:bg-blue-800" @click="borrowGear">
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
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  </Transition>
</template>
