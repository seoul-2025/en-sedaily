import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // CloudFront가 인식할 수 있도록 강제 캐싱 헤더 추가
  const response = NextResponse.next();

  const { pathname } = request.nextUrl;

  // 카테고리 페이지들 - 최신 기사 표시를 위해 캐시 비활성화
  if (
    pathname.match(
      /^\/(finance|technology|politics|society|culture|sports|international)$/
    )
  ) {
    response.headers.set(
      "Cache-Control",
      "no-cache, no-store, must-revalidate"
    );
    response.headers.set("CDN-Cache-Control", "no-cache");
    response.headers.set("Surrogate-Control", "no-cache");
    response.headers.set("X-Accel-Expires", "0");
  }

  // 메인 페이지
  if (pathname === "/") {
    response.headers.set(
      "Cache-Control",
      "public, max-age=300, s-maxage=300, stale-while-revalidate=1800"
    );
    response.headers.set("CDN-Cache-Control", "public, max-age=300");
    response.headers.set("Surrogate-Control", "public, max-age=300");
    response.headers.set("X-Accel-Expires", "300");
  }

  // 기사 상세 페이지 (레거시 URL)
  if (pathname === "/article") {
    response.headers.set(
      "Cache-Control",
      "public, max-age=3600, s-maxage=3600, stale-while-revalidate=7200"
    );
    response.headers.set("CDN-Cache-Control", "public, max-age=3600");
    response.headers.set("Surrogate-Control", "public, max-age=3600");
    response.headers.set("X-Accel-Expires", "3600");
  }

  // 기사 상세 페이지 (SEO-friendly slug-based URLs)
  // Pattern: /{category}/{year}/{month}/{day}/{slug}
  if (
    pathname.match(
      /^\/(finance|technology|politics|society|culture|sports|international|news)\/\d{4}\/\d{2}\/\d{2}\/[^/]+$/
    )
  ) {
    response.headers.set(
      "Cache-Control",
      "public, max-age=3600, s-maxage=3600, stale-while-revalidate=7200"
    );
    response.headers.set("CDN-Cache-Control", "public, max-age=3600");
    response.headers.set("Surrogate-Control", "public, max-age=3600");
    response.headers.set("X-Accel-Expires", "3600");
  }

  // 검색 페이지
  if (pathname === "/search") {
    response.headers.set(
      "Cache-Control",
      "public, max-age=180, s-maxage=180, stale-while-revalidate=900"
    );
    response.headers.set("CDN-Cache-Control", "public, max-age=180");
    response.headers.set("Surrogate-Control", "public, max-age=180");
    response.headers.set("X-Accel-Expires", "180");
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - robots.txt
     * - sitemap.xml
     */
    "/((?!api|_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml).*)",
  ],
};
