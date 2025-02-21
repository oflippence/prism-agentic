import { error } from '@sveltejs/kit';
import { PUBLIC_SITE_PASSWORD } from '$env/static/public';
import type { Actions } from './$types';

export const actions = {
    default: async ({ request, cookies }) => {
        const data = await request.formData();
        const password = data.get('password')?.toString();
        
        console.log('Server received password attempt');

        // Check if environment variable is set
        if (!PUBLIC_SITE_PASSWORD) {
            console.error('Site password not configured in environment');
            return {
                error: 'Site password not configured'
            };
        }

        // Check if password was provided
        if (!password) {
            console.error('No password provided');
            return {
                error: 'Password is required'
            };
        }

        console.log('Comparing passwords...');
        if (password === PUBLIC_SITE_PASSWORD) {
            console.log('Password correct, setting cookie');
            cookies.set('authenticated', 'true', {
                path: '/',
                httpOnly: true,
                secure: process.env.NODE_ENV === 'production',
                sameSite: 'strict',
                maxAge: 60 * 60 * 24 // 24 hours
            });

            return {
                success: true
            };
        }

        console.log('Password incorrect');
        return {
            error: 'Invalid password'
        };
    }
} satisfies Actions; 