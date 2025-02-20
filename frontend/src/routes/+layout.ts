import { browser } from '$app/environment';
import { redirect } from '@sveltejs/kit';

export const load = ({ url }: { url: URL }) => {
    // Don't protect the login page
    if (url.pathname === '/login') {
        return {};
    }

    if (browser) {
        const isAuthenticated = sessionStorage.getItem('authenticated') === 'true';
        if (!isAuthenticated) {
            throw redirect(307, `/login?returnTo=${url.pathname}`);
        }
    }

    return {};
}; 