'use client';

import { useState, useEffect } from 'react';
import { Share2, RotateCcw, Trophy, X, Clock, ExternalLink } from 'lucide-react';
import { ConnectionsPuzzle, ConnectionGroup, shuffleArray } from '@/data/connectionsPuzzles';

interface ConnectionsGameProps {
  puzzle: ConnectionsPuzzle;
}

type GameStatus = 'playing' | 'won' | 'lost';

export function ConnectionsGame({ puzzle }: ConnectionsGameProps) {
  const [items, setItems] = useState<string[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [solvedGroups, setSolvedGroups] = useState<ConnectionGroup[]>([]);
  const [mistakes, setMistakes] = useState(0);
  const [gameStatus, setGameStatus] = useState<GameStatus>('playing');
  const [showResult, setShowResult] = useState(false);
  const [shakingItems, setShakingItems] = useState<string[]>([]);
  const [timer, setTimer] = useState(0);
  const [timerEnabled, setTimerEnabled] = useState(true);

  const MAX_MISTAKES = 4;
  const ITEMS_PER_GROUP = 4;

  // Initialize game
  useEffect(() => {
    resetGame();
  }, [puzzle]);

  // Timer
  useEffect(() => {
    if (gameStatus === 'playing' && timerEnabled) {
      const interval = setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [gameStatus, timerEnabled]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const resetGame = () => {
    // Flatten all items and shuffle
    const allItems = puzzle.groups.flatMap((g) => g.items);
    setItems(shuffleArray(allItems));
    setSelected([]);
    setSolvedGroups([]);
    setMistakes(0);
    setGameStatus('playing');
    setShowResult(false);
    setShakingItems([]);
    setTimer(0);
  };

  const toggleSelect = (item: string) => {
    if (gameStatus !== 'playing') return;

    if (selected.includes(item)) {
      setSelected(selected.filter((i) => i !== item));
    } else if (selected.length < ITEMS_PER_GROUP) {
      setSelected([...selected, item]);
    }
  };

  const deselectAll = () => {
    setSelected([]);
  };

  const shuffleItems = () => {
    setItems(shuffleArray(items));
  };

  const submitGuess = () => {
    if (selected.length !== ITEMS_PER_GROUP || gameStatus !== 'playing') return;

    // Check if selection matches any unsolved group
    const matchedGroup = puzzle.groups.find((group) => {
      const groupItems = group.items.sort();
      const selectedSorted = [...selected].sort();
      return JSON.stringify(groupItems) === JSON.stringify(selectedSorted);
    });

    if (matchedGroup) {
      // Correct!
      setSolvedGroups([...solvedGroups, matchedGroup]);
      setItems(items.filter((item) => !selected.includes(item)));
      setSelected([]);

      // Check if won
      if (solvedGroups.length + 1 === puzzle.groups.length) {
        setGameStatus('won');
        setShowResult(true);
      }
    } else {
      // Incorrect - check if it's "one away"
      const oneAway = puzzle.groups.some((group) => {
        const matches = selected.filter((item) => group.items.includes(item)).length;
        return matches === 3;
      });

      // Shake animation
      setShakingItems(selected);
      setTimeout(() => setShakingItems([]), 500);

      const newMistakes = mistakes + 1;
      setMistakes(newMistakes);
      setSelected([]);

      // Check if lost
      if (newMistakes >= MAX_MISTAKES) {
        setGameStatus('lost');
        setShowResult(true);
        // Reveal all groups
        setSolvedGroups(puzzle.groups);
        setItems([]);
      }
    }
  };

  const shareResults = () => {
    const emoji = gameStatus === 'won' ? '🎉' : '😢';
    const statusText = gameStatus === 'won' ? 'Solved' : 'Failed';
    const timeStr = timerEnabled ? ` in ${formatTime(timer)}` : '';
    const result = `${emoji} K-Business Connections ${puzzle.id}\n${statusText} with ${mistakes} mistake${mistakes !== 1 ? 's' : ''}${timeStr}\n\nPlay at: ${window.location.origin}/games/connections`;

    if (navigator.share) {
      navigator.share({
        title: 'K-Business Connections',
        text: result,
      });
    } else {
      navigator.clipboard.writeText(result);
      alert('Results copied to clipboard!');
    }
  };

  const getArticleSearchLink = (group: ConnectionGroup) => {
    // 카테고리 이름으로 검색 (더 많은 결과)
    const query = group.category;
    return `/search?q=${encodeURIComponent(query)}`;
  };

  const remainingItems = items.filter((item) => !selected.includes(item));
  const availableItems = [...selected, ...remainingItems];

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header with Timer */}
      <div className="mb-8 flex items-center justify-between">
        <p className="text-gray-500 text-sm font-medium">
          Create four groups of four!
        </p>
        {timerEnabled && gameStatus === 'playing' && (
          <div className="flex items-center gap-2 text-gray-400 text-sm font-mono">
            <Clock className="w-4 h-4" />
            <span>{formatTime(timer)}</span>
          </div>
        )}
      </div>

      {/* Solved Groups */}
      {solvedGroups.map((group, idx) => (
        <div
          key={idx}
          className={`mb-2 p-5 rounded-lg ${group.color} text-white animate-fadeIn`}
        >
          <div className="flex items-center justify-between mb-1.5">
            <div className="font-bold text-sm uppercase tracking-wider opacity-90">
              {group.category}
            </div>
            <a
              href={getArticleSearchLink(group)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs opacity-75 hover:opacity-100 transition-opacity"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              Articles
            </a>
          </div>
          <div className="text-sm font-medium">
            {group.items.join(', ')}
          </div>
        </div>
      ))}

      {/* Game Board */}
      {gameStatus === 'playing' && items.length > 0 && (
        <div className="mb-8">
          <div className="grid grid-cols-4 gap-2">
            {availableItems.map((item) => {
              const isSelected = selected.includes(item);
              const isShaking = shakingItems.includes(item);

              return (
                <button
                  key={item}
                  onClick={() => toggleSelect(item)}
                  className={`
                    aspect-square flex items-center justify-center
                    rounded-md font-bold text-xs sm:text-sm
                    transition-all duration-150
                    ${
                      isSelected
                        ? 'bg-[#6374ff] text-white scale-[0.98]'
                        : 'bg-[#1a1a1a] hover:bg-[#252525] text-gray-200'
                    }
                    ${isShaking ? 'animate-shake' : ''}
                  `}
                  style={{
                    boxShadow: isSelected ? 'inset 0 -2px 0 rgba(0,0,0,0.3)' : 'inset 0 -2px 0 rgba(0,0,0,0.5)',
                    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                  }}
                >
                  <span className="px-2 text-center leading-tight">{item}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Mistakes */}
      <div className="flex justify-center gap-1.5 mb-6">
        <span className="text-sm text-gray-400 mr-2 font-medium">
          Mistakes remaining:
        </span>
        {[...Array(MAX_MISTAKES)].map((_, idx) => (
          <div
            key={idx}
            className={`w-3 h-3 rounded-full ${
              idx < mistakes ? 'bg-gray-800' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Controls */}
      {gameStatus === 'playing' && (
        <div className="flex gap-2 justify-center mb-6">
          <button
            onClick={shuffleItems}
            className="px-5 py-2.5 rounded-full bg-[#1a1a1a] hover:bg-[#252525] text-gray-300 text-sm font-semibold transition-all duration-150"
            style={{
              boxShadow: 'inset 0 -2px 0 rgba(0,0,0,0.5)',
              fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            }}
          >
            Shuffle
          </button>
          <button
            onClick={deselectAll}
            className="px-5 py-2.5 rounded-full bg-[#1a1a1a] hover:bg-[#252525] text-gray-300 text-sm font-semibold transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
            disabled={selected.length === 0}
            style={{
              boxShadow: 'inset 0 -2px 0 rgba(0,0,0,0.5)',
              fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            }}
          >
            Deselect All
          </button>
          <button
            onClick={submitGuess}
            disabled={selected.length !== ITEMS_PER_GROUP}
            className={`px-8 py-2.5 rounded-full text-sm font-semibold transition-all duration-150 ${
              selected.length === ITEMS_PER_GROUP
                ? 'bg-white text-black hover:bg-gray-200'
                : 'bg-[#252525] text-gray-600 cursor-not-allowed'
            }`}
            style={{
              boxShadow: selected.length === ITEMS_PER_GROUP ? 'inset 0 -2px 0 rgba(0,0,0,0.2)' : 'inset 0 -2px 0 rgba(0,0,0,0.5)',
              fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
            }}
          >
            Submit
          </button>
        </div>
      )}

      {/* Result Modal */}
      {showResult && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#121212] rounded-2xl p-8 max-w-md w-full border border-gray-800">
            <div className="text-center mb-6">
              {gameStatus === 'won' ? (
                <>
                  <div className="w-16 h-16 mx-auto mb-4 bg-green-500 rounded-full flex items-center justify-center">
                    <Trophy className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2" style={{
                    fontFamily: 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'
                  }}>
                    Congratulations!
                  </h3>
                  <p className="text-gray-400">
                    You solved it with {mistakes} mistake{mistakes !== 1 ? 's' : ''}
                  </p>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 mx-auto mb-4 bg-red-500 rounded-full flex items-center justify-center">
                    <X className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2" style={{
                    fontFamily: 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'
                  }}>
                    Next time!
                  </h3>
                  <p className="text-gray-400">
                    Here's the solution
                  </p>
                </>
              )}
            </div>

            {/* All Groups */}
            <div className="mb-6 space-y-2">
              {puzzle.groups.map((group, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg ${group.color} text-white text-sm`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-bold text-xs uppercase tracking-wider opacity-90">{group.category}</div>
                    <a
                      href={getArticleSearchLink(group)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs opacity-75 hover:opacity-100 transition-opacity"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Articles
                    </a>
                  </div>
                  <div className="text-sm font-medium">{group.items.join(', ')}</div>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <button
                onClick={shareResults}
                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-full font-semibold flex items-center justify-center gap-2 transition-all duration-150"
                style={{
                  boxShadow: 'inset 0 -2px 0 rgba(0,0,0,0.3)',
                  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                }}
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
              <button
                onClick={resetGame}
                className="flex-1 px-6 py-3 bg-[#1a1a1a] hover:bg-[#252525] text-gray-300 rounded-full font-semibold flex items-center justify-center gap-2 transition-all duration-150"
                style={{
                  boxShadow: 'inset 0 -2px 0 rgba(0,0,0,0.5)',
                  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
                }}
              >
                <RotateCcw className="w-4 h-4" />
                Play Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CSS for shake animation */}
      <style jsx>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
          20%, 40%, 60%, 80% { transform: translateX(4px); }
        }
        .animate-shake {
          animation: shake 0.5s;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
