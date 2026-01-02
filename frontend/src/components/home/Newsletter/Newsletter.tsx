'use client';

import { useState, FormEvent } from 'react';

export function Newsletter() {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log('Subscribe:', email);
    alert('Thank you for subscribing!');
    setEmail('');
  };

  return (
    <section className="border-t border-[var(--color-border)] pt-12 pb-16">
      <div className="max-w-2xl mx-auto text-center">
        <h3 className="font-serif text-3xl font-bold mb-4 text-[var(--color-primary)]">
          Newsletter
        </h3>
        <p className="text-lg text-[var(--color-text-light)] leading-relaxed mb-8">
          Get the latest business news and analysis delivered to your inbox every morning.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
          <input
            type="email"
            placeholder="Your email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="flex-1 px-4 py-3 border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-text)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-[var(--color-primary)] transition-colors"
          />
          <button
            type="submit"
            className="px-8 py-3 bg-[var(--color-primary)] text-white text-sm font-semibold hover:opacity-90 transition-opacity whitespace-nowrap"
          >
            Subscribe
          </button>
        </form>
      </div>
    </section>
  );
}
