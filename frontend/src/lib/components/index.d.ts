declare module '$lib/components/*.svelte' {
    import type { ComponentType } from 'svelte';
    const component: ComponentType;
    export default component;
} 