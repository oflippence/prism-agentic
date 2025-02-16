<script lang="ts">
	import Counter from '$lib/components/Counter.svelte';
	import universal from '$lib/images/6716fab0513f2918a063e314_universal.svg';
	import agents from '$lib/images/6716fb3943b30134feb5ff9a_agents.svg';
	// import Calendar from '$lib/components/Calendar.svelte';
	import Calendar2 from '$lib/components/Calendar2.svelte';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import TestComponent from '$lib/components/TestComponent.svelte';
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
		<ChatInput />
		<div class="w-full">
			<Calendar2 />
		</div>
		<!-- <Counter /> -->
		<!-- <TestComponent /> -->
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
