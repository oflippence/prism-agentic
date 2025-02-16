<script lang="ts">
	import '../app.css';
	import { AppBar } from '@skeletonlabs/skeleton';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import { onMount } from 'svelte';
	import { faSun, faMoon, faPalette } from '@fortawesome/pro-solid-svg-icons';
	import { writable } from 'svelte/store';

	const isDarkMode = writable(true);

	// Handle theme toggle
	function toggleTheme() {
		const html = document.documentElement;
		const currentTheme = html.classList.contains('dark') ? 'light' : 'dark';
		html.classList.remove('light', 'dark');
		html.classList.add(currentTheme);
		localStorage.setItem('theme', currentTheme);
		$isDarkMode = currentTheme === 'dark';
	}

	// Set dark mode by default
	onMount(() => {
		const html = document.documentElement;
		const storedTheme = localStorage.getItem('theme');
		if (!storedTheme) {
			html.classList.add('dark');
			localStorage.setItem('theme', 'dark');
			$isDarkMode = true;
		} else {
			html.classList.add(storedTheme);
			$isDarkMode = storedTheme === 'dark';
		}
	});
</script>

<!-- Root layout -->
<div class="h-full flex flex-col overflow-hidden">
	<!-- Header (fixed) -->
	<AppBar class="sticky top-0 z-10 !bg-surface-50 dark:!bg-surface-900 border-b border-surface-100 dark:border-surface-600">
		<svelte:fragment slot="lead">
			<div class="w-[100px]"><!-- Spacer to balance the layout --></div>
		</svelte:fragment>
		
		<!-- Centered navigation -->
		<div class="flex-1 flex justify-center items-center">
			<nav class="flex items-center gap-8">
				<a 
					href="/" 
					class="text-surface-900 text-base font-medium transition-colors hover:text-primary-600 dark:text-surface-50 dark:hover:text-primary-500"
				>
					Home
				</a>
				<a 
					href="https://www.universalagents.ai" 
					target="_blank"
					rel="noopener noreferrer"
					class="text-surface-900 text-base font-medium transition-colors hover:text-primary-600 dark:text-surface-50 dark:hover:text-primary-500"
				>
					About
				</a>
			</nav>
		</div>

		<svelte:fragment slot="trail">
			<div class="flex items-center gap-2 w-[100px] justify-end">
				<ThemeSwitcher>
					<button 
						class="btn-icon variant-soft hover:variant-soft-hover" 
						aria-label="Switch theme"
					>
						<svg class="w-4 h-4 text-surface-900-50-token fill-current" viewBox={`0 0 ${faPalette.icon[0]} ${faPalette.icon[1]}`}>
							<path d={String(faPalette.icon[4])} />
						</svg>
					</button>
				</ThemeSwitcher>
				<button 
					class="btn-icon variant-soft hover:variant-soft-hover" 
					on:click={toggleTheme}
					aria-label="Toggle dark mode"
				>
					<svg class="w-4 h-4 text-surface-900-50-token fill-current" viewBox={`0 0 ${$isDarkMode ? faSun.icon[0] : faMoon.icon[0]} ${$isDarkMode ? faSun.icon[1] : faMoon.icon[1]}`}>
						<path d={String($isDarkMode ? faSun.icon[4] : faMoon.icon[4])} />
					</svg>
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

	:global(.light) {
		--theme-bg: #FFFFFF;
		background-color: #FFFFFF;
	}

	:global(.light) :global(html),
	:global(.light) :global(body) {
		background-color: #FFFFFF;
	}
</style>
