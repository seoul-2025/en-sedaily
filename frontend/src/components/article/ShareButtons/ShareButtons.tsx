'use client';

import { Share2, Facebook, Twitter, Linkedin, Link as LinkIcon, Check } from 'lucide-react';
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
        const encodedDescription = encodeURIComponent(description || '');

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

    // Use native share API if available
    const handleNativeShare = async () => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title,
                    text: description,
                    url,
                });
            } catch (err) {
                console.error('Error sharing:', err);
            }
        }
    };

    return (
        <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400 mr-2">Share:</span>

            {/* Native Share (mobile) */}
            {typeof navigator !== 'undefined' && 'share' in navigator && (
                <button
                    onClick={handleNativeShare}
                    className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-dark-card hover:bg-gray-200 dark:hover:bg-dark-border rounded-lg transition-colors text-sm font-medium"
                    aria-label="Share"
                >
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                </button>
            )}

            {/* Facebook */}
            <button
                onClick={() => handleShare('facebook')}
                className="p-2 bg-[#1877F2] hover:bg-[#0d5dbb] text-white rounded-lg transition-colors"
                aria-label="Share on Facebook"
            >
                <Facebook className="w-4 h-4" />
            </button>

            {/* Twitter */}
            <button
                onClick={() => handleShare('twitter')}
                className="p-2 bg-[#1DA1F2] hover:bg-[#0d8bd9] text-white rounded-lg transition-colors"
                aria-label="Share on Twitter"
            >
                <Twitter className="w-4 h-4" />
            </button>

            {/* LinkedIn */}
            <button
                onClick={() => handleShare('linkedin')}
                className="p-2 bg-[#0A66C2] hover:bg-[#004c99] text-white rounded-lg transition-colors"
                aria-label="Share on LinkedIn"
            >
                <Linkedin className="w-4 h-4" />
            </button>

            {/* Copy Link */}
            <button
                onClick={handleCopyLink}
                className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-dark-card hover:bg-gray-200 dark:hover:bg-dark-border rounded-lg transition-colors"
                aria-label="Copy link"
            >
                {copied ? (
                    <>
                        <Check className="w-4 h-4 text-green-600" />
                        <span className="text-sm font-medium text-green-600">Copied!</span>
                    </>
                ) : (
                    <>
                        <LinkIcon className="w-4 h-4" />
                        <span className="text-sm font-medium dark:text-gray-300">Copy Link</span>
                    </>
                )}
            </button>
        </div>
    );
}
