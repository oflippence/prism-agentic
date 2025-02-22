// Environment configuration
const isDevelopment = import.meta.env.MODE === 'development';

export const config = {
  backendUrl: import.meta.env?.PUBLIC_BACKEND_URL || (
    isDevelopment 
      ? 'http://localhost:3001'
      : 'https://backend-api-736126733766.europe-west1.run.app'
  ),
  environment: import.meta.env.MODE,
  isDevelopment,
};

// Log configuration in development
if (isDevelopment) {
  console.log('[DEBUG] Environment Config:', {
    ...config,
    backendUrl: config.backendUrl,
    mode: import.meta.env.MODE,
  });
}

export default config; 