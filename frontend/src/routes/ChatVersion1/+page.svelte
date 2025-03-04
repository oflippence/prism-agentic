<script lang="ts">
	import Counter from '$lib/components/Counter.svelte';
	import universal from '$lib/images/6716fab0513f2918a063e314_universal.svg';
	import agents from '$lib/images/6716fb3943b30134feb5ff9a_agents.svg';
	// import Calendar from '$lib/components/Calendar.svelte';
	import Calendar2 from '$lib/components/Calendar2.svelte';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import TestComponent from '$lib/components/TestComponent.svelte';

	type Message = {
		question: string;
		answer: string | null;
	};

	let messages: Message[] = [];
	let error: string | null = null;

	function handleMessage(event: CustomEvent<Message>) {
		messages = [...messages, event.detail];
		error = null;
	}

	function handleUpdate(event: CustomEvent<Message>) {
		const { question, answer } = event.detail;
		messages = messages.map(msg => 
			msg.question === question ? { ...msg, answer } : msg
		);
		error = null;
	}

	function handleError(event: CustomEvent<{error: string}>) {
		error = event.detail.error;
	}
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
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
		<ChatInput 
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
						<div class="bg-surface-100-800-token p-4 rounded-container-token">
							<p class="font-semibold">You:</p>
							<p>{message.question}</p>
						</div>
						{#if message.answer === null}
							<div class="bg-primary-100 dark:bg-primary-900 p-4 rounded-container-token">
								<p class="font-semibold">Universal Agents:</p>
								<p class="text-surface-600-300-token">Thinking...</p>
							</div>
						{:else}
							<div class="bg-primary-100 dark:bg-primary-900 p-4 rounded-container-token">
								<p class="font-semibold">Universal Agents:</p>
								<p class="whitespace-pre-wrap">{message.answer}</p>
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
</style>
