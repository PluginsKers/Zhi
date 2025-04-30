<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, defineEmits } from 'vue'
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
	type: 'hello' | 'listen' | 'tts' | 'stt' | 'llm'
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
const audioContext = ref<AudioContext | null>(null)
const isPlaying = ref(false)
const opusDecoder = ref<InstanceType<typeof OpusDecoder> | null>(null)
const audioParams = ref<AudioParams | null>(null)
const lastPlaybackTime = ref(0)
const connectionState = ref<WebSocketState>('closed')
const debounceTimer = ref<number | null>(null)
const lastSendTime = ref(0)

const isConnected = computed(() => connectionState.value === 'open')
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
	const wsUrl = import.meta.env.VITE_WS_URL
	if (!wsUrl) {
		error.value = 'WebSocket URL is not configured'
		return
	}

	ws.value = new WebSocket(wsUrl)
	ws.value.binaryType = 'blob'

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
		messages.value.push(message)

		if (message.type === 'hello' && message.audio_params) {
			audioParams.value = message.audio_params
			await initAudio()
		} else if (message.type === 'tts' && message.state === 'start' && message.sample_rate) {
			await initAudio()
		}
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
}, 1000), 500)

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
	<div class="h-full w-full">
		<div class="w-full h-full overflow-y-auto">
		<div v-for="(message, index) in messages" :key="index">
			<template v-if="message.type === 'llm'">
				<span v-if="message.emotion" class="">{{ message.text }}</span>
			</template>
			<template v-else-if="message.type === 'tts' && message.state === 'sentence_start'">
				<div class="">{{ message.text }}</div>
			</template>
		</div>
	</div>
	<div class="fixed flex justify-center items-center w-full bottom-5">
		<div class="flex flex-row justify-between items-center pr-2 rounded-lg bg-gray-100 focus:bg-gray-50 ring-2 ring-gray-200 focus:ring-gray-200">
			<input v-model="inputMessage" @keyup.enter="sendMessage(inputMessage)" :placeholder="isConnected ? '输入消息' : '请稍等'"
			class="p-3 focus:outline-none  disabled:cursor-not-allowed"
			:disabled="!isConnected" />
			<button @click="sendMessage(inputMessage)" :disabled="!isConnected" class="cursor-pointer bg-black text-white flex items-center justify-center w-8 h-8 rounded-full disabled:opacity-50 disabled:cursor-not-allowed">
				<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
					<path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
				</svg>
			</button>
		</div>
	</div>
	</div>
</template>

<style></style>
