<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, defineEmits, nextTick } from 'vue'
import { OpusDecoder } from 'opus-decoder'
import type { OpusDecoderSampleRate } from 'opus-decoder'

interface AudioParams {
	format: string
	sample_rate: number
	channels: number
	frame_duration: number
}

type WebSocketState = 'connecting' | 'open' | 'closing' | 'closed'

interface ChatMessage {
	type: 'hello' | 'listen' | 'tts' | 'stt' | 'llm' | 'tts_display'
	state?: string
	text?: string
	emotion?: string
	session_id?: string
	sample_rate?: number
	version?: number
	transport?: string
	audio_params?: AudioParams
	source?: string
}

const ws = ref<WebSocket | null>(null)
const messages = ref<ChatMessage[]>([])
const error = ref<string | null>(null)
const inputMessage = ref('')
const showInput = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)
const audioContext = ref<AudioContext | null>(null)
const isPlaying = ref(false)
const opusDecoder = ref<InstanceType<typeof OpusDecoder> | null>(null)
const audioParams = ref<AudioParams | null>(null)
const lastPlaybackTime = ref(0)
const connectionState = ref<WebSocketState>('closed')
const debounceTimer = ref<number | null>(null)
const lastSendTime = ref(0)
const messageContainerRef = ref<HTMLDivElement | null>(null)

const isConnected = computed(() => connectionState.value === 'open')
const isConnecting = computed(() => connectionState.value === 'connecting')

const initAudio = async () => {
	if (!audioContext.value) {
		audioContext.value = new AudioContext()
	}
	if (!opusDecoder.value) {
		const decoder = new OpusDecoder({
			sampleRate: (audioParams.value?.sample_rate || 24000) as OpusDecoderSampleRate,
			channels: audioParams.value?.channels || 1
		})
		await decoder.ready
		opusDecoder.value = decoder
	}
}

const connectWebSocket = () => {
	const wsUrl = "wss://api.weights.chat/zhi-v1-rsa/"
	console.log('WebSocket URL:', wsUrl) // 调试信息
	
	if (!wsUrl) {
		error.value = 'WebSocket URL is not configured'
		console.error('VITE_WS_URL is not defined') // 调试信息
		return
	}

	connectionState.value = 'connecting'
	
	// 创建WebSocket连接
	ws.value = new WebSocket(wsUrl)
	ws.value.binaryType = 'blob'

	// 设置事件处理器
	ws.value.onopen = handleWebSocketOpen
	ws.value.onmessage = handleWebSocketMessage
	ws.value.onerror = handleWebSocketError
	ws.value.onclose = handleWebSocketClose
}

const handleWebSocketOpen = async () => {
	console.log('WebSocket connection established')
	error.value = null
	connectionState.value = 'open'

	const helloMessage: ChatMessage = {
		type: 'hello',
		version: 1,
		transport: 'websocket',
		audio_params: {
			format: 'opus',
			sample_rate: 48000,
			channels: 1,
			frame_duration: 60
		}
	}
	ws.value!.send(JSON.stringify(helloMessage))

	await initAudio()
}

const handleWebSocketMessage = async (event: MessageEvent) => {
	if (event.data instanceof Blob) {
		console.log('Received audio buffer')
		try {
			await playAudioBuffer(event.data)
		} catch (e) {
			console.error('Error playing audio:', e)
		}
		return
	}

	try {
		const message = JSON.parse(event.data) as ChatMessage
		
		// 处理TTS消息，从sentence_start就开始显示
		if (message.type === 'tts' && message.state === 'sentence_start' && message.text) {
			// 从sentence_start就开始显示消息
			const displayMessage: ChatMessage = {
				...message,
				state: undefined, // 移除state显示
				type: 'tts_display' // 使用特殊类型用于显示
			}
			messages.value.push(displayMessage)
		} else if (message.type === 'tts' && (message.state === 'sentence_end' || message.state === 'start' || message.state === 'stop')) {
			// 忽略sentence_end、start、stop状态，不显示这些消息
			return
		} else {
			// 其他消息正常添加
			messages.value.push(message)
		}

		if (message.type === 'hello' && message.audio_params) {
			audioParams.value = message.audio_params
			await initAudio()
		} else if (message.type === 'tts' && message.state === 'start' && message.sample_rate) {
			await initAudio()
		}
		
		// 自动滚动到底部
		nextTick(() => {
			if (messageContainerRef.value) {
				messageContainerRef.value.scrollTop = messageContainerRef.value.scrollHeight
			}
		})
	} catch (e) {
		console.error('Failed to parse message:', e)
	}
}

const emit = defineEmits(['disconnect'])

const handleWebSocketError = (event: Event) => {
	error.value = 'WebSocket error occurred'
	console.error('WebSocket error:', event)
	connectionState.value = 'closed'
	emit('disconnect')
}

const handleWebSocketClose = () => {
	console.log('WebSocket connection closed')
	connectionState.value = 'closed'
	emit('disconnect')
}

const playAudioBuffer = async (blob: Blob) => {
	if (!audioContext.value || !opusDecoder.value || !audioParams.value?.sample_rate) {
		console.error('Audio context, decoder or sample rate not initialized')
		return
	}

	try {
		if (audioContext.value.state === 'suspended') {
			await audioContext.value.resume()
		}

		isPlaying.value = true
		const arrayBuffer = await blob.arrayBuffer()

		try {
			const decodedData = await opusDecoder.value.decodeFrame(new Uint8Array(arrayBuffer))

			const audioBuffer = audioContext.value.createBuffer(
				1,
				decodedData.channelData[0].length,
				audioParams.value.sample_rate
			)

			const channelData = audioBuffer.getChannelData(0)
			for (let i = 0; i < decodedData.channelData[0].length; i++) {
				channelData[i] = decodedData.channelData[0][i]
			}

			const source = audioContext.value.createBufferSource()
			source.buffer = audioBuffer
			source.connect(audioContext.value.destination)

			const currentTime = Math.max(audioContext.value.currentTime, lastPlaybackTime.value)
			source.start(currentTime)
			lastPlaybackTime.value = currentTime + audioBuffer.duration

			await new Promise<void>((resolve) => {
				source.onended = () => {
					isPlaying.value = false
					resolve()
				}
			})
		} catch (decodeError) {
			console.error('Error decoding audio frame:', decodeError)
			isPlaying.value = false
		}
	} catch (e) {
		console.error('Error playing audio:', e)
		isPlaying.value = false
	}
}

const debounce = (fn: Function, delay: number) => {
	return (...args: any[]) => {
		if (debounceTimer.value) {
			clearTimeout(debounceTimer.value)
		}
		debounceTimer.value = window.setTimeout(() => {
			fn(...args)
			debounceTimer.value = null
		}, delay)
	}
}

const throttle = (fn: Function, limit: number) => {
        return (...args: any[]) => {
                const now = Date.now()
                if (now - lastSendTime.value >= limit) {
                        fn(...args)
                        lastSendTime.value = now
                }
        }
}

const openInput = async () => {
        showInput.value = true
        await nextTick()
        inputRef.value?.focus()
}

const sendMessage = debounce(throttle((message: string) => {
	if (!isConnected.value) {
		error.value = 'WebSocket is not connected'
		return
	}

	if (!message.trim()) {
		return
	}

	const payload: ChatMessage = {
		type: 'listen',
		state: 'detect',
		text: message,
		source: 'text'
	}
        ws.value!.send(JSON.stringify(payload))
        inputMessage.value = ''
        showInput.value = false
}, 1000), 500)

const disconnect = () => {
	if (ws.value) {
		ws.value.close()
	}
	emit('disconnect')
}

onMounted(() => {
	connectWebSocket()
})

onUnmounted(() => {
	if (ws.value) {
		ws.value.close()
	}
})
</script>

<template>
	<div class="h-full w-full flex flex-col relative">
		<!-- 扫描线效果 -->
		<div class="scanline"></div>
		
		<!-- 顶部状态栏 -->
		<div class="terminal-style p-4 border-b border-green-500">
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-4">
					<div class="flex items-center space-x-2">
						<div class="status-indicator" :class="{
							'status-connected': isConnected,
							'status-connecting': isConnecting,
							'status-disconnected': !isConnected && !isConnecting
						}"></div>
						<span class="text-green-500 text-sm font-mono">
							{{ isConnected ? 'CONNECTED' : isConnecting ? 'CONNECTING...' : 'DISCONNECTED' }}
						</span>
					</div>
					
					<div v-if="isPlaying" class="flex items-center space-x-2">
						<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
						<span class="text-green-500 text-xs font-mono">AUDIO PLAYING</span>
					</div>
				</div>
				
				<div class="flex items-center space-x-4">
					<div class="text-green-500 text-xs font-mono">
						Messages: {{ messages.length }}
					</div>
					<button @click="disconnect" class="btn-geek px-3 py-1 text-sm">
						DISCONNECT
					</button>
				</div>
			</div>
		</div>
		
		<!-- 消息区域 -->
		<div ref="messageContainerRef" class="flex-1 overflow-y-auto p-4 space-y-4">
			<div v-if="messages.length === 0" class="flex items-center justify-center h-full">
				<div class="text-center">
					<div class="text-green-500 text-lg font-mono mb-2">NO MESSAGES YET</div>
					<div class="text-green-400 text-sm opacity-60">Start a conversation...</div>
				</div>
			</div>
			
			<div v-for="(message, index) in messages" :key="index" class="message-bubble">
				<div class="flex items-start space-x-3">
					<!-- 消息类型图标 -->
					<div class="flex-shrink-0">
						<div v-if="message.type === 'llm'" class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
							<svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
								<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
							</svg>
						</div>
						<div v-else-if="message.type === 'tts' || message.type === 'tts_display'" class="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
							<svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
								<path d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"/>
							</svg>
						</div>
						<div v-else class="w-8 h-8 bg-gray-500/20 rounded-full flex items-center justify-center">
							<svg class="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
								<path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
							</svg>
						</div>
					</div>
					
					<!-- 消息内容 -->
					<div class="flex-1 min-w-0">
						<div class="flex items-center space-x-2 mb-1">
							<span class="text-green-400 text-xs font-mono uppercase">
								{{ message.type === 'tts_display' ? 'TTS' : message.type }}
							</span>
							<span v-if="message.state && message.type !== 'tts_display'" class="text-green-500 text-xs font-mono">
								[{{ message.state }}]
							</span>
							<span v-if="message.emotion" class="text-blue-400 text-xs font-mono">
								{{ message.emotion }}
							</span>
						</div>
						
						<div v-if="message.text" class="text-green-500 font-mono text-sm leading-relaxed">
							{{ message.text }}
						</div>
						
						<div v-if="message.audio_params" class="mt-2 text-xs text-green-400 opacity-60">
							<div>Format: {{ message.audio_params.format }}</div>
							<div>Sample Rate: {{ message.audio_params.sample_rate }}Hz</div>
							<div>Channels: {{ message.audio_params.channels }}</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		
		<!-- 错误提示 -->
		<div v-if="error" class="terminal-style m-4 p-3 border-red-500 border">
			<div class="flex items-center space-x-2">
				<svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
				</svg>
				<span class="text-red-500 text-sm font-mono">{{ error }}</span>
			</div>
		</div>
		
		<!-- 输入区域 -->
		<div class="terminal-style p-4 border-t border-green-500">
			<div class="flex items-center space-x-4">
				<button v-if="!showInput" @click="openInput" 
					class="btn-geek p-3 rounded-full transition-all duration-300 hover:scale-110">
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
						<path d="M17.414 2.586a2 2 0 00-2.828 0L6 11.172V14h2.828l8.586-8.586a2 2 0 000-2.828z" />
						<path fill-rule="evenodd" d="M5 18a1 1 0 001 1h3a1 1 0 001-1v-1H5v1z" clip-rule="evenodd" />
					</svg>
				</button>
				
				<div v-else class="flex-1 flex items-center space-x-2">
					<input 
						ref="inputRef" 
						v-model="inputMessage" 
						@keyup.enter="sendMessage(inputMessage)" 
						:placeholder="isConnected ? 'Type your message...' : 'Please wait...'"
						class="input-geek flex-1 p-3 rounded font-mono text-sm"
						:disabled="!isConnected" 
					/>
					<button 
						@click="sendMessage(inputMessage)" 
						:disabled="!isConnected" 
						class="btn-geek p-3 rounded transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
							<path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
						</svg>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.message-bubble {
	animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(10px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
</style>
