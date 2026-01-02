"use client";

import { Search } from "lucide-react";
import { useState, FormEvent, useRef, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";

const CATEGORIES = [
  "Markets",
  "Property",
  "Finance",
  "Business",
  "Technology",
  "Politics",
  "Society",
  "Culture",
  "Sports",
  "International",
];

export function Header() {
  const [query, setQuery] = useState("");
  const [isScrolled, setIsScrolled] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Ball position state
  const [ballPosition, setBallPosition] = useState<number | null>(null);
  const [isHovering, setIsHovering] = useState(false);
  const navRef = useRef<HTMLUListElement>(null);
  const itemRefs = useRef<(HTMLLIElement | null)[]>([]);

  // Scroll detection
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Find active category index
  const activeIndex = CATEGORIES.findIndex(
    (item) => pathname === `/${item.toLowerCase()}`
  );

  // Update ball position based on hover or active state
  const updateBallPosition = (index: number) => {
    const item = itemRefs.current[index];
    const nav = navRef.current;
    if (item && nav) {
      const navRect = nav.getBoundingClientRect();
      const itemRect = item.getBoundingClientRect();
      const position = itemRect.left - navRect.left + itemRect.width / 2;
      setBallPosition(position);
    }
  };

  // Set initial ball position for active category
  useEffect(() => {
    if (activeIndex >= 0 && !isHovering) {
      updateBallPosition(activeIndex);
    }
  }, [activeIndex, isHovering]);

  const handleMouseEnter = (index: number) => {
    setIsHovering(true);
    updateBallPosition(index);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    // Return to active category or hide
    if (activeIndex >= 0) {
      updateBallPosition(activeIndex);
    } else {
      setBallPosition(null);
    }
  };

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <>
      {/* 1영역: Seoul Economic Daily - Sticky on mobile */}
      <div className="sticky top-0 md:static bg-[var(--color-bg)] z-30 md:z-auto">
        <div className="max-w-container mx-auto px-gutter pt-12 pb-4">
          <Link
            href="/"
            className="text-3xl md:text-5xl font-serif font-normal tracking-normal text-[var(--color-text)] hover:text-[var(--color-brand-blue)] transition-colors block text-center" style={{fontFamily: 'Georgia, "Times New Roman", Times, serif'}}
          >
            Seoul Economic Daily
          </Link>
        </div>
      </div>

      {/* 2영역: 검색창, 로고 */}
      <div className="bg-[var(--color-bg)] border-b border-[var(--color-border)]">
        <div className="max-w-container mx-auto px-gutter py-1 md:py-3">
          <div className="flex items-center justify-between">
            {/* Search Bar - Left */}
            <form
              onSubmit={handleSearch}
              className="flex items-center border-b border-[var(--color-border)] pb-1 w-48 md:w-64 focus-within:border-[var(--color-text-light)] transition-colors"
            >
              <input
                type="text"
                name="search"
                id="search-input"
                placeholder="Search..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="bg-transparent border-none outline-none text-sm w-full placeholder-[var(--color-text-muted)] text-[var(--color-text)]"
                style={{ outline: "none", boxShadow: "none" }}
                aria-label="Search articles"
              />
              <button
                type="submit"
                aria-label="Search"
                className="outline-none hidden"
                style={{ outline: "none" }}
              >
                <Search className="w-4 h-4 text-[var(--color-text-light)] hover:text-[var(--color-text)] transition-colors" />
              </button>
            </form>

            {/* Seoul Economic Link - Right */}
            <a
              href="https://www.sedaily.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:opacity-80 transition-opacity"
              aria-label="Visit Seoul Economic Daily main site"
            >
              <img
                src="/sedaily-logo.jpg"
                alt="Seoul Economic Daily"
                className="w-24 h-16 object-contain"
              />
            </a>
          </div>
        </div>
      </div>

      {/* 3영역: 카테고리 목록 - Sticky on both mobile and desktop */}
      <div className={`sticky top-[88px] md:top-0 bg-[var(--color-bg)] z-20 border-b border-[var(--color-border)] ${isScrolled ? 'border-t' : ''}`}>
        <nav
          role="navigation"
          aria-label="Main navigation"
        >
          <div className="max-w-container mx-auto px-8">
            <ul
              ref={navRef}
              className="flex md:justify-between overflow-x-auto md:overflow-x-visible relative scrollbar-hide"
              style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
              onMouseLeave={handleMouseLeave}
            >
              {CATEGORIES.map((item, index) => {
                const isActive = pathname === `/${item.toLowerCase()}`;
                return (
                  <li
                    key={item}
                    ref={(el) => { itemRefs.current[index] = el; }}
                    className="relative"
                    onMouseEnter={() => handleMouseEnter(index)}
                  >
                    <Link
                      href={`/${item.toLowerCase()}`}
                      prefetch={true}
                      className={`block px-3 md:px-2 pt-2 pb-3 md:pt-2 md:pb-3 text-base font-medium transition-colors whitespace-nowrap text-center drop-shadow-lg ${
                        isActive
                          ? "text-[var(--color-brand-blue)] font-bold drop-shadow-xl"
                          : "text-[var(--color-text)] hover:text-[var(--color-brand-blue)] hover:drop-shadow-xl"
                      }`}
                    >
                      {item}
                    </Link>
                  </li>
                );
              })}

              {/* Animated ball indicator (sedaily.com style) */}
              {(ballPosition !== null) && (
                <span
                  className="absolute w-2 h-2 bg-[#0066cc] rounded-full pointer-events-none"
                  style={{
                    left: `${ballPosition}px`,
                    bottom: "-4px",
                    transform: "translateX(-50%)",
                    opacity: isHovering || activeIndex >= 0 ? 1 : 0,
                    transition: "left 0.25s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s ease",
                  }}
                />
              )}
            </ul>
          </div>
        </nav>
      </div>
    </>
  );
}
