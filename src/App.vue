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
  <div class="min-h-screen w-full relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="fixed inset-0 pointer-events-none">
      <!-- 网格背景 -->
      <div class="absolute inset-0 opacity-5">
        <div class="grid-pattern"></div>
      </div>
      
      <!-- 角落装饰 -->
      <div class="absolute top-0 left-0 w-32 h-32 border-l-2 border-t-2 border-green-500 opacity-30"></div>
      <div class="absolute top-0 right-0 w-32 h-32 border-r-2 border-t-2 border-green-500 opacity-30"></div>
      <div class="absolute bottom-0 left-0 w-32 h-32 border-l-2 border-b-2 border-green-500 opacity-30"></div>
      <div class="absolute bottom-0 right-0 w-32 h-32 border-r-2 border-b-2 border-green-500 opacity-30"></div>
      
      <!-- 浮动粒子效果 -->
      <div class="floating-particles"></div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="relative z-10 h-screen">
      <Starter v-if="!showChat" @start="handleStart" />
      <Chat v-else @disconnect="handleDisconnect" />
    </div>
    
    <!-- 系统状态栏 -->
    <div class="fixed top-0 left-0 right-0 z-20">
      <div class="bg-black/80 backdrop-blur-sm border-b border-green-500/30 p-2">
        <div class="flex items-center justify-between text-green-500 text-xs font-mono">
          <div class="flex items-center space-x-4">
            <span>ZHI AI SYSTEM</span>
            <span>v1.0.0</span>
            <span class="status-dot"></span>
            <span>ONLINE</span>
          </div>
          <div class="flex items-center space-x-4">
            <span>{{ new Date().toLocaleTimeString() }}</span>
            <span>CPU: 12%</span>
            <span>MEM: 2.4GB</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-pattern {
  background-image: 
    linear-gradient(rgba(0, 255, 65, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 65, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
  width: 100%;
  height: 100%;
}

.floating-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(2px 2px at 20px 30px, rgba(0, 255, 65, 0.3), transparent),
    radial-gradient(2px 2px at 40px 70px, rgba(0, 255, 65, 0.2), transparent),
    radial-gradient(1px 1px at 90px 40px, rgba(0, 255, 65, 0.4), transparent),
    radial-gradient(1px 1px at 130px 80px, rgba(0, 255, 65, 0.2), transparent),
    radial-gradient(2px 2px at 160px 30px, rgba(0, 255, 65, 0.3), transparent);
  background-repeat: repeat;
  background-size: 200px 100px;
  animation: float 20s linear infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-100px); }
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #00ff41;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
