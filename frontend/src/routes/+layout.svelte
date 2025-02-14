<script lang="ts">
	import '../app.css';
	import { AppShell, AppBar } from '@skeletonlabs/skeleton';

	// Handle theme toggle
	function toggleTheme() {
		const html = document.documentElement;
		const currentTheme = html.classList.contains('dark') ? 'light' : 'dark';
		html.classList.remove('light', 'dark');
		html.classList.add(currentTheme);
		localStorage.setItem('theme', currentTheme);
	}
</script>

<!-- App Shell -->
<AppShell>
	<svelte:fragment slot="header">
		<!-- App Bar -->
		<AppBar class="fixed top-0 left-0 right-0 z-10 px-4">
			<svelte:fragment slot="lead">
				<strong class="text-xl uppercase">My App</strong>
			</svelte:fragment>
			<svelte:fragment slot="trail">
				<div class="flex items-center gap-4">
					<a class="btn btn-sm variant-ghost-surface" href="/">Home</a>
					<a class="btn btn-sm variant-ghost-surface" href="/about">About</a>
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
	</svelte:fragment>
	<!-- Page Route Content -->
	<main class="container mx-auto p-4 pt-20 space-y-8 w-full">
		<slot />
	</main>
</AppShell>

<style>
	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		max-width: 64rem;
		box-sizing: border-box;
	}

	@media (min-width: 480px) {
		
	}
</style>
