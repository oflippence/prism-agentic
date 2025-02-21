import { dev } from '$app/environment';

// we don't need any JS on this page, though we'll load
// it in dev so that we get hot module replacement
export const csr = dev;

// This page requires authentication, so we can't prerender it
export const ssr = true;
