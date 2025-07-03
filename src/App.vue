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
  <div class="min-h-screen flex flex-col">
    <div class="flex-grow flex items-center justify-center p-4 bg-white">
      <Starter v-if="!showChat" @start="handleStart" />
      <Chat v-else @disconnect="handleDisconnect" />
    </div>
  </div>
</template>

<style scoped></style>
