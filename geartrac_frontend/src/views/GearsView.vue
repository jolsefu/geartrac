<script setup>
import { ref } from 'vue'
import { api } from '@/api'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

const isVisible = ref()
const gears = ref()
const gearIds = ref()
const currentGear = ref({})

setTimeout(() => {
  isVisible.value = true
}, 200)

const getGears = async () => {
  try {
    const response = await api.get('gear/')
    gears.value = response.data
  } catch (error) {
    console.log(error)
  }
}

function handleCheckboxChange(id, event)
{
  if (event.target.checked) {
    gearIds.value.push(id)
  } else {
    gearIds.value = gearIds.value.filter(gearId => gearId !== id)
  }
}

getGears()

</script>

<template>
  <transition name="swipe-up">
    <div v-if="isVisible" class="flex items-center justify-center h-screen text-center flex-col">
      <Dialog>
        <div class="container mx-auto px-4 max-w-4xl mt-16">
          <div v-for="gear in gears" :key="gear.property_number" class="mb-4 p-4 border rounded shadow flex">
            <div class="flex items-center">
              <label>
                <input type="checkbox" :value="gear" @change="handleCheckboxChange(gear.id, $event)" />
              </label>
            </div>

            <div class="border-r border-gray-300 mx-4"></div>

            <h2>
              <DialogTrigger as-child>
                <Button class="bg-white text-black hover:bg-[#cccccc] hover:text-black" @click="currentGear.value = gear">
                  {{ gear.name }}
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
              <div v-if="!currentGear.value.used && !currentGear.value.borrowed" class="text-white">This gear is available.</div>
              <br>
              <div> {{ currentGear.value.unit_description }} </div>
              <div> Owner: {{ currentGear.value.owner }} </div>
              <div v-if="currentGear.value.used_by"> Used by: {{ currentGear.value.used_by }}</div>
              <div v-if="currentGear.value.borrowed_by"> Borrowed by: {{ currentGear.value.borrowed_by }}</div>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>

      </Dialog>
    </div>
  </transition>

</template>
