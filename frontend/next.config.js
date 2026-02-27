/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  /**
   * Rewrite /api/:path* → BACKEND_URL/api/:path*
   *
   * This acts as a safety net for any request that reaches Next.js but has
   * no matching app/api/ route file.  The Next.js App Router always resolves
   * app/api/ handlers first, so existing proxy routes are unaffected.
   *
   * Required Railway env var on the FRONTEND service:
   *   BACKEND_URL=https://<your-backend-service>.up.railway.app
   *
   * If BACKEND_URL is not set the rewrite list is empty and the app still
   * boots — the app/api/ proxy routes remain the primary path.
   */
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_URL ||
      process.env.BACKEND_API_URL ||
      '';

    if (!backendUrl) {
      console.warn(
        '[next.config] BACKEND_URL is not set — /api/* rewrites disabled. ' +
        'Set BACKEND_URL in Railway → frontend service → Variables.'
      );
      return [];
    }

    const base = backendUrl.replace(/\/$/, '');

    return [
      {
        source: '/api/:path*',
        destination: `${base}/api/:path*`,
      },
    ];
  },

  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
