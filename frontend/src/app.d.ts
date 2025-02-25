/// <reference types="@sveltejs/kit" />
/// <reference types="svelte" />
/// <reference path="./lib/skeleton-types.d.ts" />
/// <reference path="./lib/svelte-types.d.ts" />

import { SupabaseClient, Session } from '@supabase/supabase-js'

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			supabase: SupabaseClient
			getSession(): Promise<Session | null>
		}
		interface PageData {
			session: Session | null
		}
		// interface Platform {}
	}
}

// Svelte HTML declarations
declare namespace svelte.JSX {
	interface HTMLAttributes<T> {
		'on:click'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
		'on:change'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
		'on:keydown'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
		'on:keyup'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
		'on:focus'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
		'on:blur'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
		'on:submit'?: (event: CustomEvent<any> & { target: EventTarget & T }) => void;
	}
}

export {};
