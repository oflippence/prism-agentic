<!-- frontend/src/routes/login/+page.svelte -->
<script lang="ts">
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import { PUBLIC_SITE_PASSWORD } from '$env/static/public';
    import { faEye, faEyeSlash } from '@fortawesome/pro-solid-svg-icons';
    
    let password = '';
    let error = '';
    let showPassword = false;

    async function handleSubmit() {
        console.log('Entered password:', password);
        console.log('Expected password:', PUBLIC_SITE_PASSWORD);
        
        if (password === PUBLIC_SITE_PASSWORD) {
            if (browser) {
                sessionStorage.setItem('authenticated', 'true');
                const returnUrl = new URLSearchParams(window.location.search).get('returnTo') || '/';
                goto(returnUrl);
            }
        } else {
            error = 'Invalid password';
            password = '';
        }
    }

    function togglePasswordVisibility() {
        showPassword = !showPassword;
    }
</script>

<!-- Override the default container -->
<div class="absolute inset-0 -mt-[64px] pt-[64px]">
    <div class="relative h-full flex items-center justify-center p-4">
        <div class="card p-8 w-full max-w-md space-y-6">
            <div class="text-center">
                <h2 class="h2 mb-2">Protected Site</h2>
                <p class="text-surface-600-300-token">Please enter the password to access this site</p>
            </div>
            
            <form class="space-y-6" on:submit|preventDefault={handleSubmit}>
                <div class="relative">
                    <input
                        class="input p-4 text-lg w-full pr-12"
                        type={showPassword ? 'text' : 'password'}
                        bind:value={password}
                        required
                        placeholder="Site password"
                    />
                    <button
                        type="button"
                        class="btn-icon absolute right-3 top-1/2 -translate-y-1/2 variant-soft hover:variant-soft-hover"
                        on:click={togglePasswordVisibility}
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                        <svg 
                            class="w-5 h-5 text-surface-900-50-token fill-current" 
                            viewBox={`0 0 ${showPassword ? faEyeSlash.icon[0] : faEye.icon[0]} ${showPassword ? faEyeSlash.icon[1] : faEye.icon[1]}`}
                        >
                            <path d={String(showPassword ? faEyeSlash.icon[4] : faEye.icon[4])} />
                        </svg>
                    </button>
                </div>

                {#if error}
                    <div class="text-error-500-400-token text-sm">{error}</div>
                {/if}

                <button type="submit" class="btn variant-filled-primary w-full p-4">
                    Access Site
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

    /* Match the button icon styling from your chat input */
    :global(.btn-icon.variant-soft) {
        @apply bg-surface-100 hover:bg-surface-300;
    }

    :global(.dark) :global(.btn-icon.variant-soft) {
        @apply bg-surface-600 hover:bg-surface-500;
    }
</style> 