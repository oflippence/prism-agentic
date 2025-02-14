declare module '@skeletonlabs/skeleton' {
    import type { SvelteComponent } from 'svelte';
    import type { Action } from 'svelte/action';
    
    export class AppBar extends SvelteComponent {}
    export class AppShell extends SvelteComponent {}
    export class ProgressBar extends SvelteComponent<{value?: number}> {}
    export class Datepicker extends SvelteComponent<{
        value?: Date;
        format?: string;
        closeOnSelect?: boolean;
    }> {}
    
    export interface PopupSettings {
        event: 'focus-click' | 'hover' | 'click';
        target: string;
        placement?: 'top' | 'bottom' | 'left' | 'right';
    }
    
    export const popup: Action<HTMLElement, PopupSettings>;
    
    // Add any other Skeleton components you're using
} 