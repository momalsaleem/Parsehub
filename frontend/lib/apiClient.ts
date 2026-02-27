import axios, { AxiosInstance, AxiosError } from 'axios';
import { getApiBaseUrl } from './apiBase';

/**
 * Enhanced API Client for ParseHub internal application
 * - Automatically resolves the correct backend URL
 * - Handles authentication headers injections
 * - Provides graceful error handling across the app
 */

// 1. Resolve and Validate Base URL
// `getApiBaseUrl()` from your new centralized config already does production checks!
const baseURL = getApiBaseUrl();

// 2. Initialize Axios instance
export const apiClient: AxiosInstance = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds timeout
});

// 3. Request Interceptor: Attach Auth Token dynamically if needed
apiClient.interceptors.request.use((config) => {
    // We attach the PARSEHUB_API_KEY from env, as previously seen across the codebase.
    const apiKey = process.env.NEXT_PUBLIC_API_KEY || 't_hmXetfMCq3';
    if (apiKey && config.headers) {
        config.headers['Authorization'] = `Bearer ${apiKey}`;
    }
    return config;
}, (error) => Promise.reject(error));

// 4. Response Interceptor: Graceful Error Handling for Unreachable Backend
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        // Determine if the error is a network connection failure (Backend Unreachable)
        const isNetworkError =
            error.message === 'Network Error' ||
            error.code === 'ECONNREFUSED' ||
            error.code === 'ENOTFOUND' ||
            error.code === 'ECONNABORTED';

        if (isNetworkError) {
            console.error('[API Client] CRITICAL: Backend is unreachable at', baseURL);

            // Inject a user-friendly error payload that the UI can detect
            return Promise.reject({
                isNetworkError: true,
                message: 'Backend API is currently unreachable. Please check your network connection or try again later.',
                originalError: error
            });
        }

        // Pass through standard HTTP errors (400s, 500s)
        const errorData = error.response?.data || {};
        const errorMsg = (errorData as any).error || (errorData as any).details || `HTTP ${error.response?.status} ${error.response?.statusText}`;

        return Promise.reject({
            isNetworkError: false,
            message: errorMsg,
            status: error.response?.status,
            originalError: error,
            data: errorData
        });
    }
);

export default apiClient;
