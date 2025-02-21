/// <reference types="vite/client" />

declare module '$env/static/public' {
    export const PUBLIC_SITE_PASSWORD: string;
}

interface ImportMetaEnv {
    readonly PUBLIC_SITE_PASSWORD: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
} 