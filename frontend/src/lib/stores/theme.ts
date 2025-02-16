import { writable } from 'svelte/store';

// Define available themes
export const themes = [
    'universal-agents',
    'skeleton',
    'wintry',
    'modern',
    'rocket',
    'seafoam',
    'vintage',
    'sahara',
    'hamlindigo',
    'gold-nouveau',
    'crimson'
] as const;

export type Theme = typeof themes[number];

// Initialize theme from localStorage or default to 'universal-agents'
const storedTheme = typeof localStorage !== 'undefined' ? localStorage.getItem('app-theme') as Theme : 'universal-agents';
const initialTheme = themes.includes(storedTheme as Theme) ? storedTheme : 'universal-agents';

export const currentTheme = writable<Theme>(initialTheme);

// Subscribe to theme changes and update localStorage and body classes
if (typeof document !== 'undefined') {
    currentTheme.subscribe((theme) => {
        localStorage.setItem('app-theme', theme);
        document.body.setAttribute('data-theme', theme);
    });
} 