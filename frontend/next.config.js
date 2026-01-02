/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  // output: 'export', // EC2 서버 모드를 위해 제거
  output: 'standalone', // EC2 배포용
  compress: true,
  poweredByHeader: false,
  reactStrictMode: isProd, // 개발 모드에서는 false로 설정하여 이중 호출 및 참조 오류 방지
  swcMinify: isProd,       // Windows 개발 환경에서 'call' 에러 방지를 위해 개발 중에는 false

  experimental: {
    optimizePackageImports: ['lucide-react'],
    esmExternals: false // Windows 경로 문제 해결
  },

  compiler: {
    removeConsole: isProd ? {
      exclude: ['error', 'warn']
    } : false
  },

  images: {
    domains: ['newsimg.sedaily.com', 'd39c7rf2w6v6qi.cloudfront.net'],
    unoptimized: false 
  },

  // Windows 경로 및 모듈 참조 문제 해결을 위한 webpack 설정
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

  // 정적 에셋 캐싱 및 보안 헤더
  async headers() {
    // 개발 모드에서는 엄격한 CSP 헤더 때문에 'call' 에러가 날 수 있으므로 배포 때만 적용
    if (!isProd) return [];

    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google.com *.googletagmanager.com *.googlesyndication.com *.google-analytics.com pagead2.googlesyndication.com",
              "style-src 'self' 'unsafe-inline' fonts.googleapis.com",
              "font-src 'self' fonts.gstatic.com",
              "img-src 'self' data: https: *.sedaily.com *.cloudfront.net *.google-analytics.com *.googletagmanager.com *.googlesyndication.com",
              "connect-src 'self' *.execute-api.us-east-1.amazonaws.com *.google-analytics.com *.analytics.google.com *.googletagmanager.com",
              "frame-src 'self' https://www.youtube.com https://tv.naver.com *.googlesyndication.com",
              "media-src 'self' https:",
              "object-src 'none'",
              "base-uri 'self'",
              "form-action 'self'",
              "frame-ancestors 'self'",
              "upgrade-insecure-requests"
            ].join('; ')
          }
        ]
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=600, stale-while-revalidate=3600'
          }
        ]
      },
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      },
      {
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