<script setup>
import { ref, reactive } from "vue";
import { authLogIn, authLogOut, isAuthenticated, userDetails, authNotify } from "@/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Notify from "@/components/Notify.vue";

const isVisible = ref(false);

setTimeout(() => {
  isVisible.value = true;
}, 200);
</script>

<template>
  <Notify :notify="authNotify" />

  <Transition name="swipe-up">
    <div v-if="isVisible" class="flex justify-center h-screen pt-[8rem] max-w">
      <Card class="w-fit h-fit">
        <CardHeader v-if="!isAuthenticated">
          <CardTitle>Login to GearTRAC</CardTitle>
          <CardDescription>You must login via carsu.edu.ph emails!</CardDescription>
        </CardHeader>
        <CardHeader v-else>
          <CardTitle>Welcome to GearTRAC, {{ userDetails.first_name }}!</CardTitle>
          <CardDescription>Logged in as {{ userDetails.email }}</CardDescription>
        </CardHeader>
        <CardContent class="flex gap-1">
          <div class="flex flex-col gap-1">
            <div>
              <Button
                v-if="!isAuthenticated"
                @click="authLogIn"
                class="bg-white text-black hover:bg-[#cccccc]"
              >
                <i class="material-icons">domain</i>
                Login With @carsu.edu.ph
              </Button>
            </div>
            <div>
              <Button @click="authLogOut" class="!bg-[#ad0000] hover:!bg-[#990000]"
                >Logout</Button
              >
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </Transition>
</template>
