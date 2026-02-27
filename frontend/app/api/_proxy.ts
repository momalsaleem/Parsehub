/**
 * _proxy.ts — Central server-side proxy utility
 *
 * All Next.js API route handlers call `proxyToBackend()` from here.
 * The browser NEVER calls the Flask domain directly — it only ever hits
 * /api/* on the same Next.js origin, eliminating CORS entirely.
 *
 * BACKEND_API_URL is a server-only env var (no NEXT_PUBLIC prefix).
 * It is never baked into the client bundle.
 */

import { NextRequest, NextResponse } from 'next/server';

const TIMEOUT_MS = 30_000;

// ─── Backend URL resolution ────────────────────────────────────────────────
function getBackendUrl(): string {
    const url =
        process.env.BACKEND_API_URL ||
        process.env.BACKEND_URL ||
        'http://localhost:5000';

    if (process.env.NODE_ENV === 'production') {
        if (!process.env.BACKEND_API_URL && !process.env.BACKEND_URL) {
            throw new Error(
                '[proxy] BACKEND_API_URL is not set. ' +
                'Add it to Railway → frontend service → Variables.'
            );
        }
        if (
            url.includes('localhost') ||
            url.includes('127.0.0.1') ||
            url.includes('0.0.0.0')
        ) {
            throw new Error(
                `[proxy] BACKEND_API_URL resolves to a local address in production: ${url}`
            );
        }
    }

    return url.replace(/\/$/, ''); // strip trailing slash
}

const BACKEND_BASE = getBackendUrl();
const BACKEND_API_KEY = process.env.BACKEND_API_KEY || 't_hmXetfMCq3';

// ─── Core proxy function ───────────────────────────────────────────────────
/**
 * Forward a Next.js route request to the Flask backend.
 *
 * @param request  - The incoming NextRequest
 * @param backendPath - Path on the Flask backend, e.g. "/api/projects"
 * @param queryOverrides - Optional URLSearchParams to use instead of the
 *                         request's own search params
 */
export async function proxyToBackend(
    request: NextRequest,
    backendPath: string,
    queryOverrides?: URLSearchParams
): Promise<NextResponse> {
    const qs = queryOverrides ?? request.nextUrl.searchParams;
    const queryString = qs.toString();
    const targetUrl = `${BACKEND_BASE}${backendPath}${queryString ? `?${queryString}` : ''}`;

    const method = request.method.toUpperCase();
    console.log(`[proxy] ${method} ${request.nextUrl.pathname} → ${targetUrl}`);

    // Forward the request body for mutating methods
    let body: string | undefined;
    if (!['GET', 'HEAD', 'DELETE'].includes(method)) {
        try {
            body = await request.text();
        } catch {
            body = undefined;
        }
    }

    // Build outgoing headers
    const outgoingHeaders: Record<string, string> = {
        'Authorization': `Bearer ${BACKEND_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

    try {
        const backendResponse = await fetch(targetUrl, {
            method,
            headers: outgoingHeaders,
            body: body || undefined,
            signal: controller.signal,
        });

        clearTimeout(timer);

        // Try to parse JSON; fall back to text
        const contentType = backendResponse.headers.get('content-type') ?? '';
        let responseData: unknown;
        if (contentType.includes('application/json')) {
            responseData = await backendResponse.json();
        } else {
            responseData = { raw: await backendResponse.text() };
        }

        if (!backendResponse.ok) {
            console.error(
                `[proxy] Backend returned ${backendResponse.status} for ${targetUrl}`
            );
            return NextResponse.json(
                {
                    error: (responseData as Record<string, string>)?.error ??
                        `Backend error ${backendResponse.status}`,
                },
                { status: backendResponse.status }
            );
        }

        return NextResponse.json(responseData, { status: backendResponse.status });

    } catch (err: unknown) {
        clearTimeout(timer);

        if (err instanceof Error && err.name === 'AbortError') {
            console.error(`[proxy] Timeout after ${TIMEOUT_MS}ms for ${targetUrl}`);
            return NextResponse.json(
                { error: 'Backend request timed out. Please try again.' },
                { status: 504 }
            );
        }

        console.error(`[proxy] Network error reaching ${targetUrl}:`, err);
        return NextResponse.json(
            {
                error: 'Backend is unreachable. Check BACKEND_API_URL and ensure the Flask service is running.',
                details: err instanceof Error ? err.message : String(err),
            },
            { status: 502 }
        );
    }
}
