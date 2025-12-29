import { revalidatePath } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

// Category mapping: Korean to English
const CATEGORY_MAP: Record<string, string> = {
  '경제': 'finance',
  'IT_과학': 'technology',
  '정치': 'politics',
  '사회': 'society',
  '문화': 'culture',
  '스포츠': 'sports',
  '국제': 'international',
  '지역': 'society',
};

export async function POST(request: NextRequest) {
  try {
    // Verify secret
    const secret = request.headers.get('x-revalidate-secret');
    const expectedSecret = process.env.REVALIDATE_SECRET;

    if (!expectedSecret) {
      console.error('REVALIDATE_SECRET not configured');
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      );
    }

    if (secret !== expectedSecret) {
      console.warn('Invalid revalidation secret received');
      return NextResponse.json(
        { error: 'Invalid secret' },
        { status: 401 }
      );
    }

    // Parse request body
    const body = await request.json();
    const { type, category, slug, publishedAt, path } = body;

    console.log('Revalidation request:', { type, category, slug, publishedAt, path });

    const revalidatedPaths: string[] = [];

    // Revalidate specific path if provided
    if (path) {
      revalidatePath(path);
      revalidatedPaths.push(path);
      console.log('Revalidated specific path:', path);
    }

    // Revalidate article detail page
    if (type === 'article' && slug && publishedAt && category) {
      const [year, month, day] = publishedAt.split('T')[0].split('-');
      const englishCategory = CATEGORY_MAP[category] || 'news';
      const articlePath = `/${englishCategory}/${year}/${month}/${day}/${slug}`;

      revalidatePath(articlePath);
      revalidatedPaths.push(articlePath);
      console.log('Revalidated article path:', articlePath);
    }

    // Revalidate category page
    if (category) {
      const englishCategory = CATEGORY_MAP[category] || 'news';
      const categoryPath = `/${englishCategory}`;

      revalidatePath(categoryPath);
      revalidatedPaths.push(categoryPath);
      console.log('Revalidated category path:', categoryPath);
    }

    // Revalidate home page
    revalidatePath('/');
    revalidatedPaths.push('/');
    console.log('Revalidated home path: /');

    return NextResponse.json({
      revalidated: true,
      paths: revalidatedPaths,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Revalidation error:', error);
    return NextResponse.json(
      { error: 'Revalidation failed', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
