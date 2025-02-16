<!-- ThemeSwitcher.svelte -->
<script lang="ts">
    import { currentTheme, themes, type Theme } from '$lib/stores/theme';

    let isOpen = false;

    function handleThemeSelect(theme: Theme) {
        currentTheme.set(theme);
        isOpen = false;
    }

    function handleClickOutside(event: MouseEvent) {
        const target = event.target as HTMLElement;
        if (!target.closest('.theme-switcher')) {
            isOpen = false;
        }
    }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="theme-switcher relative">
    <button
        class="btn btn-sm variant-ghost-surface"
        on:click={() => isOpen = !isOpen}
        aria-label="Select theme"
        aria-expanded={isOpen}
        aria-controls="theme-menu"
    >
        🎨
    </button>

    {#if isOpen}
        <div
            id="theme-menu"
            class="card variant-filled-surface p-2 w-48 shadow-xl fixed mt-1 z-[999]"
            role="menu"
            style="position: absolute; top: 100%; right: 0;"
        >
            <nav class="list-nav">
                <ul class="space-y-1">
                    {#each themes as theme}
                        <li>
                            <a
                                href="javascript:void(0)"
                                class="block px-4 py-2 hover:variant-soft-primary rounded-token"
                                class:!variant-soft-primary={$currentTheme === theme}
                                on:click={() => handleThemeSelect(theme)}
                                role="menuitem"
                            >
                                {theme}
                            </a>
                        </li>
                    {/each}
                </ul>
            </nav>
        </div>
    {/if}
</div>

<style>
    .theme-switcher {
        position: relative;
    }
</style> 