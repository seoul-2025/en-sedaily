'use client';

import { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Pause, Play } from 'lucide-react';

interface ArticleAudioPlayerProps {
  content: string;
  title: string;
}

export function ArticleAudioPlayer({ content, title }: ArticleAudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    // Check if browser supports Web Speech API
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setIsSupported(true);
    }

    // Cleanup on unmount
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handlePlay = () => {
    if (!isSupported) {
      alert('Your browser does not support text-to-speech feature.');
      return;
    }

    // Resume if paused
    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    // Clean text: remove excessive newlines and whitespace
    const cleanText = `${title}. ${content}`
      .replace(/\n{3,}/g, '\n\n')
      .replace(/\s+/g, ' ')
      .trim();

    // Create new utterance
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'en-US';
    utterance.rate = 1.0; // Normal speed
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Set voice (prefer female US English voice)
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(
      (voice) =>
        voice.lang === 'en-US' &&
        (voice.name.includes('Female') || voice.name.includes('Samantha'))
    ) || voices.find((voice) => voice.lang === 'en-US');

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    // Event handlers
    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
      utteranceRef.current = null;
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsPlaying(false);
      setIsPaused(false);
      utteranceRef.current = null;
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const handlePause = () => {
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    window.speechSynthesis.cancel();
    setIsPlaying(false);
    setIsPaused(false);
    utteranceRef.current = null;
  };

  if (!isSupported) {
    return null; // Don't render if not supported
  }

  return (
    <div className="flex items-center gap-2">
      {!isPlaying && !isPaused && (
        <button
          onClick={handlePlay}
          className="flex items-center gap-2 px-3 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="Listen to article"
          title="Listen to article"
        >
          <Volume2 className="w-4 h-4" />
          <span className="text-sm font-medium hidden sm:inline">Listen</span>
        </button>
      )}

      {isPlaying && (
        <button
          onClick={handlePause}
          className="flex items-center gap-2 px-3 py-2 bg-[var(--color-accent)] text-white hover:opacity-90 rounded-lg transition-colors"
          aria-label="Pause"
          title="Pause"
        >
          <Pause className="w-4 h-4" />
          <span className="text-sm font-medium hidden sm:inline">Pause</span>
        </button>
      )}

      {isPaused && (
        <button
          onClick={handlePlay}
          className="flex items-center gap-2 px-3 py-2 bg-[var(--color-accent)] text-white hover:opacity-90 rounded-lg transition-colors"
          aria-label="Resume"
          title="Resume"
        >
          <Play className="w-4 h-4" />
          <span className="text-sm font-medium hidden sm:inline">Resume</span>
        </button>
      )}

      {(isPlaying || isPaused) && (
        <button
          onClick={handleStop}
          className="flex items-center gap-2 px-2 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="Stop"
          title="Stop"
        >
          <VolumeX className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
