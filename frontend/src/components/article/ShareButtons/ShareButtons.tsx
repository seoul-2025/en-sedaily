'use client';

import { Facebook, Twitter, Linkedin, Link as LinkIcon, Check } from 'lucide-react';
import { useState } from 'react';

interface ShareButtonsProps {
    title: string;
    url: string;
    description?: string;
}

export function ShareButtons({ title, url, description }: ShareButtonsProps) {
    const [copied, setCopied] = useState(false);

    const handleCopyLink = async () => {
        try {
            await navigator.clipboard.writeText(url);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy link:', err);
        }
    };

    const handleShare = (platform: string) => {
        const encodedUrl = encodeURIComponent(url);
        const encodedTitle = encodeURIComponent(title);

        let shareUrl = '';

        switch (platform) {
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`;
                break;
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`;
                break;
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`;
                break;
        }

        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }
    };

    return (
        <div className="flex items-center gap-3">
            {/* Facebook */}
            <button
                onClick={() => handleShare('facebook')}
                className="text-[var(--color-text-light)] hover:text-[var(--color-accent)] transition-colors"
                aria-label="Share on Facebook"
                title="Facebook"
            >
                <Facebook className="w-4 h-4" />
            </button>

            {/* Twitter */}
            <button
                onClick={() => handleShare('twitter')}
                className="text-[var(--color-text-light)] hover:text-[var(--color-accent)] transition-colors"
                aria-label="Share on Twitter"
                title="Twitter"
            >
                <Twitter className="w-4 h-4" />
            </button>

            {/* LinkedIn */}
            <button
                onClick={() => handleShare('linkedin')}
                className="text-[var(--color-text-light)] hover:text-[var(--color-accent)] transition-colors"
                aria-label="Share on LinkedIn"
                title="LinkedIn"
            >
                <Linkedin className="w-4 h-4" />
            </button>

            {/* Copy Link */}
            <button
                onClick={handleCopyLink}
                className={`transition-colors ${
                    copied ? 'text-green-600' : 'text-[var(--color-text-light)] hover:text-[var(--color-accent)]'
                }`}
                aria-label="Copy link"
                title={copied ? "Copied!" : "Copy URL"}
            >
                {copied ? (
                    <Check className="w-4 h-4" />
                ) : (
                    <LinkIcon className="w-4 h-4" />
                )}
            </button>
        </div>
    );
}
