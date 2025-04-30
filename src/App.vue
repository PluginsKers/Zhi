<script setup lang="ts">
import { ref } from 'vue'
import Starter from './components/Starter.vue'
import Chat from './components/Chat.vue'

const showChat = ref(false)

const handleStart = () => {
  showChat.value = true
}

const handleDisconnect = () => {
  showChat.value = false
}
</script>

<template>
  <div class="grow flex flex-col">
    <div class="relative grow flex flex-col mx-auto w-full overflow-hidden h-[0px]">
      <div class="fixed inset-0 p-4 flex items-center justify-center bg-white">
        <Starter v-if="!showChat" @start="handleStart" />
        <Chat v-else @disconnect="handleDisconnect" />
      </div>
    </div>
  </div>
</template>

<style scoped></style>
