<script setup>
import { ref } from 'vue'
import { authLogIn, authLogOut, authTest } from '@/auth'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const isVisible = ref(false)

setTimeout(() => {
  isVisible.value = true
}, 200)
</script>

<template>
  <transition name="swipe-up">
    <div v-if="isVisible" class="flex justify-center h-screen pt-[8rem] max-w">
      <Card class="w-full sm:w-3/4 md:w-1/2 xl:w-fit h-fit m-4">
        <CardHeader>
          <CardTitle>Login to GearTRAC</CardTitle>
          <CardDescription>You must login via carsu.edu.ph emails!</CardDescription>
        </CardHeader>
        <CardContent class="flex gap-1">
          <div class="flex flex-col gap-1">
            <div>
              <Button @click="authLogIn">
                <i class="material-icons">domain</i>
                Login With @carsu.edu.ph
              </Button>
            </div>
            <div>
              <Button @click="authLogOut" class="!bg-[#ad0000] hover:!bg-[#990000]">Logout</Button>
            </div>
          </div>
          <div>
            <Button @click="authTest">Test Authentication</Button>
          </div>
        </CardContent>
      </Card>

    </div>
  </transition>
 </template>
