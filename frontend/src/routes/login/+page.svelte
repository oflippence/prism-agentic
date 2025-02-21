<!-- frontend/src/routes/login/+page.svelte -->
<script lang="ts">
    import { enhance } from '$app/forms';
    import { faEye, faEyeSlash } from '@fortawesome/pro-solid-svg-icons';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import type { ActionResult } from '@sveltejs/kit';
    
    let password = '';
    let showPassword = false;
    let returnUrl = '/';
    let isSubmitting = false;

    export let form: { error?: string; success?: boolean } | null = null;

    onMount(() => {
        returnUrl = new URLSearchParams(window.location.search).get('returnTo') || '/';
    });

    function handleEnhance() {
        return async ({ result, update }: { result: ActionResult, update: () => Promise<void> }) => {
            isSubmitting = true;
            console.log('Starting form submission');
            
            try {
                await update();
                console.log('Form submission result:', result);
                
                if (form?.error) {
                    console.log('Form has error:', form.error);
                    password = '';
                } else {
                    console.log('No form error, attempting login');
                    if (browser) {
                        console.log('Setting session storage and redirecting');
                        sessionStorage.setItem('authenticated', 'true');
                        await goto(returnUrl);
                    }
                }
            } catch (err) {
                console.error('Error during form submission:', err);
                password = '';
            } finally {
                isSubmitting = false;
            }
        };
    }
</script>

<div class="absolute inset-0 -mt-[64px] pt-[64px]">
    <div class="relative h-full flex items-center justify-center p-4">
        <div class="card p-8 w-full max-w-md space-y-6">
            <div class="text-center">
                <h2 class="h2 mb-2">Protected Site</h2>
                <p class="text-surface-600-300-token">Please enter the password to access this site</p>
            </div>
            
            <form 
                method="POST" 
                class="space-y-6" 
                use:enhance={handleEnhance}
            >
                <div class="relative">
                    <input
                        class="input p-4 text-lg w-full pr-12"
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        bind:value={password}
                        required
                        placeholder="Site password"
                        disabled={isSubmitting}
                    />
                    <input 
                        type="hidden" 
                        name="returnUrl" 
                        bind:value={returnUrl}
                    />
                    <button
                        type="button"
                        class="btn-icon absolute right-3 top-1/2 -translate-y-1/2 variant-soft hover:variant-soft-hover"
                        on:click={() => showPassword = !showPassword}
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                        disabled={isSubmitting}
                    >
                        <svg 
                            class="w-5 h-5 text-surface-900-50-token fill-current" 
                            viewBox={`0 0 ${showPassword ? faEyeSlash.icon[0] : faEye.icon[0]} ${showPassword ? faEyeSlash.icon[1] : faEye.icon[1]}`}
                        >
                            <path d={String(showPassword ? faEyeSlash.icon[4] : faEye.icon[4])} />
                        </svg>
                    </button>
                </div>

                {#if form?.error}
                    <div class="text-error-500-400-token text-sm">{form.error}</div>
                {/if}

                <button 
                    type="submit" 
                    class="btn variant-filled-primary w-full p-4"
                    disabled={isSubmitting}
                >
                    {isSubmitting ? 'Verifying...' : 'Access Site'}
                </button>
            </form>
        </div>
    </div>
</div>

<style>
    .input {
        min-height: 3rem;
    }
    
    .card {
        background-color: rgb(var(--color-surface-500) / 0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgb(var(--color-surface-500) / 0.2);
        border-radius: 0.5rem;
    }

    :global(.btn-icon.variant-soft) {
        @apply bg-surface-100 hover:bg-surface-300;
    }

    :global(.dark) :global(.btn-icon.variant-soft) {
        @apply bg-surface-600 hover:bg-surface-500;
    }
</style> 