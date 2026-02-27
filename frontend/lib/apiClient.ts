/**
 * apiClient.ts — Browser-side Axios client
 *
 * baseURL is intentionally EMPTY ("") so every request goes to the
 * same-origin Next.js server (/api/projects, /api/metadata, etc.).
 *
 * Next.js route handlers then proxy server-to-server to the Flask backend.
 * The browser NEVER touches the Flask domain — eliminating all CORS issues.
 *
 * NEXT_PUBLIC_API_BASE_URL is no longer needed or used here.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// baseURL must be empty so all requests go to same origin (Next.js)
const apiClient: AxiosInstance = axios.create({
    baseURL: '',   // <-- same-origin: browser -> Next.js /api/* routes
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30_000,
});

// Response interceptor — turn network/connection errors into readable messages
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        const isNetworkError =
            error.message === 'Network Error' ||
            error.code === 'ECONNREFUSED' ||
            error.code === 'ENOTFOUND' ||
            error.code === 'ECONNABORTED';

        if (isNetworkError) {
            console.error('[apiClient] Network error — backend unreachable');
            return Promise.reject({
                isNetworkError: true,
                message: 'Backend API is currently unreachable. Please check your connection or try again later.',
                originalError: error,
            });
        }

        const errorData = error.response?.data ?? {};
        const errorMsg =
            (errorData as Record<string, string>).error ??
            (errorData as Record<string, string>).details ??
            `HTTP ${error.response?.status} ${error.response?.statusText}`;

        return Promise.reject({
            isNetworkError: false,
            message: errorMsg,
            status: error.response?.status,
            originalError: error,
            data: errorData,
        });
    }
);

export default apiClient;
