/// <reference types="svelte" />

type EventHandler<E extends Event = Event, T extends Element = Element> = (event: E & { currentTarget: EventTarget & T }) => void;

declare module "svelte/elements" {
  export interface HTMLAttributes<T extends EventTarget> {
    'on:click'?: EventHandler<MouseEvent, T>;
    'on:change'?: EventHandler<Event, T>;
    'on:keydown'?: EventHandler<KeyboardEvent, T>;
    'on:keyup'?: EventHandler<KeyboardEvent, T>;
    'on:focus'?: EventHandler<FocusEvent, T>;
    'on:blur'?: EventHandler<FocusEvent, T>;
    'on:submit'?: EventHandler<SubmitEvent, T>;
  }
} 