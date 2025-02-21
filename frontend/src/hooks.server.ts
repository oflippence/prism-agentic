import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
    const path = event.url.pathname;
    console.log(`Processing request for path: ${path}`);

    // Don't protect the login page
    if (path === '/login') {
        console.log('Login page accessed, proceeding without auth check');
        return await resolve(event);
    }

    // Check authentication
    const authenticated = event.cookies.get('authenticated') === 'true';
    console.log(`Auth check for ${path} - Cookie authenticated: ${authenticated}`);
    
    if (!authenticated) {
        console.log(`Not authenticated, redirecting to login from ${path}`);
        const redirectUrl = `/login?returnTo=${path}`;
        console.log(`Redirect URL: ${redirectUrl}`);
        
        return new Response(null, {
            status: 303,
            headers: {
                Location: redirectUrl
            }
        });
    }

    console.log(`User authenticated, proceeding with request to ${path}`);
    return await resolve(event);
}; 