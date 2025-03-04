<script lang="ts">
	import Counter from '$lib/components/Counter.svelte';
	import universal from '$lib/images/6716fab0513f2918a063e314_universal.svg';
	import agents from '$lib/images/6716fb3943b30134feb5ff9a_agents.svg';
	// import Calendar from '$lib/components/Calendar.svelte';
	import Calendar2 from '$lib/components/Calendar2.svelte';
	import ChatInputV2 from '$lib/components/ChatInputV2.svelte';
	import TestComponent from '$lib/components/TestComponent.svelte';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	type Message = {
		question: string | null;  // Updated to allow null for welcome message
		answer: string | null;
	};

	let messages: Message[] = [];
	let error: string | null = null;

	// Function to safely convert markdown to HTML
	function convertMarkdownToHtml(markdown: string): string {
		// Convert markdown to HTML using synchronous marked.parse
		const rawHtml = marked.parse(markdown, { async: false }) as string;
		// Sanitize the HTML to prevent XSS attacks
		const cleanHtml = DOMPurify.sanitize(rawHtml);
		return cleanHtml;
	}

	function handleMessage(event: CustomEvent<Message>) {
		console.log('[DEBUG] Received message event:', event.detail);
		messages = [...messages, event.detail];
		error = null;
	}

	function handleUpdate(event: CustomEvent<Message>) {
		console.log('[DEBUG] Received update event:', event.detail);
		const { question, answer } = event.detail;
		
		// For welcome message (no question), replace any existing welcome message
		if (!question) {
			console.log('[DEBUG] Handling welcome message update');
			// Remove any existing welcome messages (those with no question)
			messages = messages.filter(msg => msg.question !== null);
			// Add the new welcome message
			messages = [...messages, event.detail];
		} else {
			// For regular messages, update existing one
			console.log('[DEBUG] Handling regular message update');
			messages = messages.map(msg => 
				msg.question === question ? { ...msg, answer } : msg
			);
		}
		error = null;
	}

	function handleError(event: CustomEvent<{error: string}>) {
		console.error('[DEBUG] Received error event:', event.detail);
		error = event.detail.error;
	}
</script>

<svelte:head>
	<title>PRISM</title>
	<meta name="description" content="PRISM AI Assistant" />
</svelte:head>

<section class="w-full">
	<h1 class="mt-16 lg:mt-24 mb-16 lg:mb-24">
		<span class="logo">
			<div class="flex flex-col sm:flex-row items-center justify-center gap-0 sm:gap-6">
				<img 
					src={universal} 
					alt="Universal" 
					class="w-[300px] sm:w-[400px] lg:w-[500px] max-w-full" 
				/>
				<img 
					src={agents} 
					alt="Agents" 
					class="w-[225px] sm:w-[300px] lg:w-[375px] max-w-full translate-y-[16px] -mt-2 sm:mt-0" 
				/>
			</div>
		</span>
	</h1>

	<div class="space-y-8 lg:space-y-12 w-full">
		<ChatInputV2 
			on:message={handleMessage} 
			on:update={handleUpdate}
			on:error={handleError} 
		/>
		
		{#if error}
			<div class="w-full p-4 bg-red-100 text-red-700 rounded-container-token">
				{error}
			</div>
		{/if}

		{#if messages.length > 0}
			<div class="w-full space-y-6">
				{#each messages as message}
					<div class="w-full space-y-4">
						{#if message.question}
							<div class="bg-surface-100-800-token p-4 rounded-container-token">
								<p class="font-semibold">You:</p>
								<p>{message.question}</p>
							</div>
						{/if}
						{#if message.answer === null}
							<div class="bg-primary-100 dark:bg-primary-900 p-4 rounded-container-token">
								<p class="font-semibold">PRISM:</p>
								<p class="text-surface-600-300-token">Thinking...</p>
							</div>
						{:else}
							<div class="bg-primary-100 dark:bg-primary-900 p-4 rounded-container-token">
								<p class="font-semibold">PRISM:</p>
								<div class="prose prose-sm dark:prose-invert max-w-none">
									{@html convertMarkdownToHtml(message.answer)}
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}

	</div>
</section>

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}

	h1 {
		width: 100%;
	}

	.logo {
		display: block;
		width: 100%;
	}

	/* Add styles for markdown content */
	:global(.prose) {
		@apply text-base leading-7;
	}

	:global(.prose h1) {
		@apply text-2xl font-bold mt-6 mb-4;
	}

	:global(.prose h2) {
		@apply text-xl font-bold mt-5 mb-3;
	}

	:global(.prose h3) {
		@apply text-lg font-bold mt-4 mb-2;
	}

	:global(.prose ul) {
		@apply list-disc pl-6 mb-4;
	}

	:global(.prose ol) {
		@apply list-decimal pl-6 mb-4;
	}

	:global(.prose li) {
		@apply mb-1;
	}

	:global(.prose p) {
		@apply mb-4;
	}

	:global(.prose code) {
		@apply bg-surface-200-700-token px-1 py-0.5 rounded;
	}

	:global(.prose pre) {
		@apply bg-surface-200-700-token p-4 rounded mb-4 overflow-x-auto;
	}

	:global(.prose blockquote) {
		@apply border-l-4 border-surface-300-600-token pl-4 italic my-4;
	}
</style>