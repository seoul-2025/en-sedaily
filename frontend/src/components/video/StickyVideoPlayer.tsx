'use client';

import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

interface StickyVideoPlayerProps {
  videoUrl: string;
  originalVideoRef?: React.RefObject<HTMLDivElement>; // Optional now
  alwaysVisible?: boolean; // New prop for homepage
}

export function StickyVideoPlayer({ videoUrl, originalVideoRef, alwaysVisible = false }: StickyVideoPlayerProps) {
  const [isSticky, setIsSticky] = useState(alwaysVisible);
  const [isClosed, setIsClosed] = useState(false);

  useEffect(() => {
    // If alwaysVisible is true, don't use IntersectionObserver
    if (alwaysVisible) {
      setIsSticky(true);
      return;
    }

    if (!originalVideoRef?.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        // 원본 동영상이 화면에서 벗어나면 sticky 활성화
        setIsSticky(!entry.isIntersecting);
      },
      {
        threshold: 0,
        rootMargin: '-100px 0px 0px 0px' // 100px 위로 스크롤하면 활성화
      }
    );

    observer.observe(originalVideoRef.current);

    return () => {
      observer.disconnect();
    };
  }, [originalVideoRef, alwaysVisible]);

  // Extract video ID from Naver TV URL
  const videoId = videoUrl.match(/\/v\/(\d+)/)?.[1];
  if (!videoId) return null;

  // 닫혔거나 sticky 상태가 아니면 렌더링 안 함
  if (isClosed || !isSticky) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slideInUp">
      <div className="relative w-[320px] bg-black rounded-lg shadow-2xl overflow-hidden">
        {/* Close Button */}
        <button
          onClick={() => setIsClosed(true)}
          className="absolute top-2 right-2 z-10 w-8 h-8 flex items-center justify-center bg-black/70 hover:bg-black/90 rounded-full text-white transition-colors"
          aria-label="Close video"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Video Player */}
        <div className="relative" style={{ paddingBottom: '56.25%', height: 0 }}>
          <iframe
            src={`https://tv.naver.com/embed/${videoId}?autoPlay=true`}
            className="absolute top-0 left-0 w-full h-full"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
          />
        </div>
      </div>

      <style jsx>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-slideInUp {
          animation: slideInUp 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
