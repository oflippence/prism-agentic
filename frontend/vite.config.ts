import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Load env file based on `mode` in the current working directory.
	// Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
	const env = loadEnv(mode, process.cwd(), '');
	
	return {
		plugins: [sveltekit()],
		// Vite config
		define: {
			'process.env': env
		},
		server: {
			port: 5173,
			strictPort: false,
		},
		optimizeDeps: {
			exclude: ['@skeletonlabs/skeleton']
		}
	};
});
