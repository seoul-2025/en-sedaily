/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export', // EC2 서버 모드를 위해 제거
  output: 'standalone', // EC2 배포용
  compress: true,
  poweredByHeader: false,
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizePackageImports: ['lucide-react'],
    esmExternals: false // Windows 경로 문제 해결
  },
  compiler: {
    removeConsole: false // Temporarily disabled for debugging
  },
  images: {
    domains: ['newsimg.sedaily.com', 'd39c7rf2w6v6qi.cloudfront.net'],
    unoptimized: false // 서버 모드에서는 이미지 최적화 가능
  },
  // Windows 경로 문제 해결을 위한 webpack 설정
  webpack: (config, { isServer }) => {
    if (process.platform === 'win32') {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        os: false,
      };
    }
    return config;
  },
  // 정적 에셋 캐싱만 유지 (middleware에서 HTML 캐싱 처리)
  async headers() {
    return [
      {
        // API 라우트들
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=600, stale-while-revalidate=3600'
          }
        ]
      },
      {
        // 정적 에셋들
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      },
      {
        // _next 정적 파일들
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      }
    ]
  }
};

module.exports = nextConfig;
