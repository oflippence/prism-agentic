import { browser } from '$app/environment';
import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ url }) => {
    // Don't protect the login page
    if (url.pathname === '/login') {
        return {};
    }

    // Only check sessionStorage in the browser
    if (browser && sessionStorage.getItem('authenticated') !== 'true') {
        throw redirect(303, `/login?returnTo=${url.pathname}`);
    }

    return {};
}; 