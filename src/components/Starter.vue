<script setup lang="ts">
const emit = defineEmits(['start'])
</script>

<template>
  <div class="flex flex-col items-center gap-4" style="will-change: auto; transform: none;">
    <img src="/logo.svg" alt="Zhi Logo" class="w-24 h-24" />
    <button @click="emit('start')"
      class="cursor-pointer justify-center whitespace-nowrap rounded-none text-lg font-normal border-2 border-green-500 bg-black text-green-500 hover:bg-black/80 h-10 px-5 py-2 flex items-center gap-2">
      <span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          class="lucide lucide-phone size-4 opacity-50">
          <path
            d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
        </svg>
      </span>
      <span>开始</span>
    </button>
  </div>
</template>

<style scoped></style>
