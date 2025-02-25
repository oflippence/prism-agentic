import { browser } from '$app/environment';
import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';
import { createClient } from '$lib/supabase/_archive/client'
import type { Session } from '@supabase/supabase-js'

export const load: LayoutLoad = async ({ url, depends }) => {
    // Don't protect the login page
    if (url.pathname === '/login') {
        return {
            session: null
        }
    }

    // Only check sessionStorage in the browser
    if (browser && sessionStorage.getItem('authenticated') !== 'true') {
        throw redirect(303, `/login?returnTo=${url.pathname}`);
    }

    depends('supabase:auth')

    const supabase = createClient()

    const {
        data: { session },
    } = await supabase.auth.getSession()

    return {
        supabase,
        session
    }
}; 