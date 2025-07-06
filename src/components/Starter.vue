<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Emits {
  (e: 'start'): void
}

const emit = defineEmits<Emits>()
const isReady = ref(false)
const terminalText = ref('')
const fullText = 'SYSTEM INITIALIZED...\nREADY TO CONNECT\n> PRESS START TO BEGIN'

onMounted(() => {
  typeText()
})

const typeText = () => {
  let index = 0
  const typeInterval = setInterval(() => {
    if (index < fullText.length) {
      terminalText.value += fullText[index]
      index++
    } else {
      clearInterval(typeInterval)
      setTimeout(() => {
        isReady.value = true
      }, 500)
    }
  }, 50)
}
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-4 relative">
    <!-- 扫描线效果 -->
    <div class="scanline"></div>
    
    <!-- 背景网格 -->
    <div class="absolute inset-0 opacity-10">
      <div class="grid-pattern"></div>
    </div>
    
    <!-- 主容器 -->
    <div class="terminal-style rounded-lg p-8 max-w-md w-full relative z-10">
      <!-- 终端标题栏 -->
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-green-500">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 bg-red-500 rounded-full"></div>
          <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <div class="w-3 h-3 bg-green-500 rounded-full"></div>
        </div>
        <div class="text-green-500 text-sm font-mono">ZHI AI TERMINAL v1.0</div>
      </div>
      
      <!-- Logo区域 -->
      <div class="flex flex-col items-center mb-8">
        <div class="relative mb-4">
          <img src="/logo.svg" alt="Zhi Logo" class="w-20 h-20 filter drop-shadow-lg" />
          <div class="absolute inset-0 w-20 h-20 border-2 border-green-500 rounded-full animate-pulse"></div>
        </div>
        <h1 class="text-2xl font-bold text-green-500 mb-2 tracking-wider">ZHI AI</h1>
        <p class="text-green-400 text-sm opacity-80">Advanced AI Communication System</p>
      </div>
      
      <!-- 终端输出 -->
      <div class="bg-black/50 p-4 rounded border border-green-500 mb-6 font-mono text-sm">
        <div class="text-green-500 whitespace-pre-line">{{ terminalText }}<span class="animate-blink">|</span></div>
      </div>
      
      <!-- 状态指示器 -->
      <div class="flex items-center justify-center mb-6">
        <div class="status-indicator" :class="isReady ? 'status-connected' : 'status-connecting'"></div>
        <span class="text-green-500 text-sm font-mono">
          {{ isReady ? 'SYSTEM READY' : 'INITIALIZING...' }}
        </span>
      </div>
      
      <!-- 开始按钮 -->
      <button 
        @click="emit('start')"
        :disabled="!isReady"
        class="btn-geek w-full py-4 px-6 text-lg font-mono tracking-wider relative overflow-hidden transition-all duration-300"
        :class="{ 'opacity-50 cursor-not-allowed': !isReady, 'terminal-glow': isReady }"
      >
        <span class="relative z-10 flex items-center justify-center space-x-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="animate-pulse">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
          <span>{{ isReady ? 'START CONNECTION' : 'INITIALIZING...' }}</span>
        </span>
      </button>
      
      <!-- 系统信息 -->
      <div class="mt-6 text-center">
        <div class="text-green-400 text-xs opacity-60 space-y-1">
          <div>Protocol: WebSocket v1.0</div>
          <div>Audio Codec: Opus</div>
          <div>Security: TLS 1.3</div>
        </div>
      </div>
    </div>
    
    <!-- 装饰性元素 -->
    <div class="absolute top-4 right-4 text-green-500 text-xs opacity-40 font-mono">
      <div>CPU: 100%</div>
      <div>MEM: 64GB</div>
      <div>NET: 1Gbps</div>
    </div>
    
    <div class="absolute bottom-4 left-4 text-green-500 text-xs opacity-40 font-mono">
      <div>UPTIME: 00:00:00</div>
      <div>CONNECTIONS: 0</div>
    </div>
  </div>
</template>

<style scoped>
.grid-pattern {
  background-image: 
    linear-gradient(rgba(0, 255, 65, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 65, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  width: 100%;
  height: 100%;
}

.animate-blink {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
