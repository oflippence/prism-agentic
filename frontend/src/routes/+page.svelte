<script lang="ts">
	import Counter from '$lib/components/Counter.svelte';
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';
	import Calendar from '$lib/components/Calendar.svelte';
	import Calendar2 from '$lib/components/Calendar2.svelte';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import TestComponent from '$lib/components/TestComponent.svelte';
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<section class="w-full">
	<h1>
		<span class="welcome">
			<picture>
				<source srcset={welcome} type="image/webp" />
				<img src={welcomeFallback} alt="Welcome" />
			</picture>
		</span>

		to your new<br />SvelteKit app
	</h1>

	<h2>
		try editing <strong>src/routes/+page.svelte</strong>
	</h2>

	<div class="space-y-6 w-full">
		<ChatInput />
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<div>
				<h3 class="h3 mb-2">Flatpickr Calendar</h3>
				<Calendar />
			</div>
			<div>
				<h3 class="h3 mb-2">DaisyUI Calendar</h3>
				<Calendar2 />
			</div>
		</div>
		<Counter />
		<TestComponent />
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

	.welcome {
		display: block;
		position: relative;
		width: 100%;
		height: 0;
		padding: 0 0 calc(100% * 495 / 2048) 0;
	}

	.welcome img {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		display: block;
	}
</style>
