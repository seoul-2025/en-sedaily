'use client';

import { useState } from 'react';
import Image from 'next/image';

interface ArticleImageProps {
  imageUrl: string;
  title: string;
  category?: string;
  originalLink?: string;
}

export function ArticleImage({ imageUrl, title, category, originalLink }: ArticleImageProps) {
  const [imageError, setImageError] = useState(false);

  // SEO-optimized alt text with category and source information
  const altText = category
    ? `${title} - Seoul Economic Daily ${category} News from South Korea`
    : `${title} - Seoul Economic Daily News from South Korea`;

  if (imageError && originalLink) {
    return (
      <div className="mb-8">
        <a
          href={originalLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[var(--color-accent)] hover:underline text-sm"
        >
          View images in original article →
        </a>
      </div>
    );
  }

  return (
    <figure className="mb-8">
      <div className="relative w-full h-96 rounded-lg overflow-hidden">
        <Image
          src={imageUrl}
          alt={altText}
          title={title}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 100vw, 768px"
          priority
          onError={() => setImageError(true)}
        />
      </div>
      <figcaption className="text-[11px] text-gray-500 mt-2 text-center italic">
        {title} - Seoul Economic Daily{category ? ` ${category}` : ''}
      </figcaption>
    </figure>
  );
}