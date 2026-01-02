'use client';

import { useRef } from 'react';
import { StickyVideoPlayer } from './StickyVideoPlayer';

interface VideoSectionProps {
  naverTvUrl: string;
}

export function VideoSection({ naverTvUrl }: VideoSectionProps) {
  const videoContainerRef = useRef<HTMLDivElement>(null);

  const videoId = naverTvUrl.match(/\/v\/(\d+)/)?.[1];
  if (!videoId) return null;

  return (
    <>
      <div ref={videoContainerRef} className="mt-8 mb-8">
        <h3 className="text-xl font-bold mb-4 text-[var(--color-primary)]">
          Related Video
        </h3>
        <div
          className="relative"
          style={{ paddingBottom: "56.25%", height: 0 }}
        >
          <iframe
            src={`https://tv.naver.com/embed/${videoId}?autoPlay=false`}
            className="absolute top-0 left-0 w-full h-full rounded-lg"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
          />
        </div>
      </div>

      <StickyVideoPlayer
        videoUrl={naverTvUrl}
        originalVideoRef={videoContainerRef}
      />
    </>
  );
}
