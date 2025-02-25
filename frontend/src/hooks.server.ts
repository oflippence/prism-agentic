import { createServerClient } from '@supabase/ssr'
import type { Handle } from '@sveltejs/kit'

export const handle: Handle = async ({ event, resolve }) => {
  event.locals.supabase = createServerClient(
    process.env.PUBLIC_SUPABASE_URL!,
    process.env.PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get: (key) => event.cookies.get(key),
        set: (key, value, options) => {
          event.cookies.set(key, value, { ...options, path: '/' })
        },
        remove: (key, options) => {
          event.cookies.delete(key, { ...options, path: '/' })
        },
      },
    }
  )

  /**
   * A convenience helper so we can just call await getSession()
   */
  event.locals.getSession = async () => {
    const {
      data: { session },
    } = await event.locals.supabase.auth.getSession()
    return session
  }

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
  return await resolve(event, {
    filterSerializedResponseHeaders(name) {
      return name === 'content-range'
    },
  });
} 