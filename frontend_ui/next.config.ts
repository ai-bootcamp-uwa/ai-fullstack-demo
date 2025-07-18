import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    BACKEND_GATEWAY_URL: process.env.BACKEND_GATEWAY_URL || 'http://localhost:3003',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3003',
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${process.env.BACKEND_GATEWAY_URL || 'http://localhost:3003'}/api/backend/:path*`,
      },
    ];
  },
};

export default nextConfig;
