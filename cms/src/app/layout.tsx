import './globals.css';

export const metadata = {
  title: 'SEOdaily CMS',
  description: 'Content Management System',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  );
}
