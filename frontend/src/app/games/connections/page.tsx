import { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Info, Gamepad2 } from "lucide-react";
import { ConnectionsGame } from "@/components/games/ConnectionsGame";
import { getPuzzleByDate } from "@/data/connectionsPuzzles";
import { PageTransition } from "@/components/PageTransition";

export const metadata: Metadata = {
  title: "K-Business Connections - Seoul Economic Daily",
  description: "Group 16 Korean companies into 4 categories. Test your knowledge of Korean business!",
};

export default function ConnectionsPage() {
  const puzzle = getPuzzleByDate();

  return (
    <PageTransition>
      <div className="min-h-screen py-6 px-4" style={{
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div className="max-w-2xl mx-auto">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-all duration-200 font-medium text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Link>

        {/* Header */}
        <header className="text-center mb-10">
          <h1 className="text-5xl md:text-6xl font-black text-white mb-3 tracking-tight" style={{
            fontFamily: 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
            letterSpacing: '-0.02em'
          }}>
            Connections
          </h1>
          <p className="text-gray-400 text-base font-medium">
            Group four Korean companies by category
          </p>
        </header>

        {/* Game */}
        <ConnectionsGame puzzle={puzzle} />

        {/* How to Play */}
        <div className="mt-12 p-6 bg-[#121212] border border-gray-800 rounded-xl">
          <h3 className="text-base font-bold text-white mb-4" style={{
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
          }}>
            How to Play
          </h3>
          <div className="text-sm text-gray-400 space-y-2.5 font-medium">
            <p>Find groups of four companies that share something in common</p>
            <p>Select four companies and tap Submit to check your guess</p>
            <p>You have 4 mistakes before the game ends</p>
            <p>Categories include industries, business types, and more</p>
          </div>
        </div>
        </div>
      </div>
    </PageTransition>
  );
}
