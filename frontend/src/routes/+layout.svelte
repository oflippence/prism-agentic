<script lang="ts">
	import '../app.css';
	import { AppBar } from '@skeletonlabs/skeleton';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import { onMount } from 'svelte';

	// Handle theme toggle
	function toggleTheme() {
		const html = document.documentElement;
		const currentTheme = html.classList.contains('dark') ? 'light' : 'dark';
		html.classList.remove('light', 'dark');
		html.classList.add(currentTheme);
		localStorage.setItem('theme', currentTheme);
	}

	// Set dark mode by default
	onMount(() => {
		const html = document.documentElement;
		const storedTheme = localStorage.getItem('theme');
		if (!storedTheme) {
			html.classList.add('dark');
			localStorage.setItem('theme', 'dark');
		} else {
			html.classList.add(storedTheme);
		}
	});
</script>

<!-- Root layout -->
<div class="h-full flex flex-col overflow-hidden">
	<!-- Header (fixed) -->
	<AppBar class="sticky top-0 z-10">
		<svelte:fragment slot="lead">
			<strong class="text-xl uppercase">My App</strong>
		</svelte:fragment>
		<svelte:fragment slot="trail">
			<div class="flex items-center gap-4">
				<a class="btn btn-sm variant-ghost-surface" href="/">Home</a>
				<a class="btn btn-sm variant-ghost-surface" href="/about">About</a>
				<ThemeSwitcher />
				<button 
					class="btn btn-sm variant-ghost-surface" 
					on:click={toggleTheme}
					aria-label="Toggle theme"
				>
					🌓
				</button>
			</div>
		</svelte:fragment>
	</AppBar>

	<!-- Main Content (scrollable) -->
	<main class="flex-1 overflow-y-auto w-full">
		<div class="container mx-auto px-4 py-4 space-y-8 max-w-7xl">
			<slot />
		</div>
	</main>
</div>

<style>
	:global(html, body) {
		@apply h-full overflow-hidden;
	}
</style>
