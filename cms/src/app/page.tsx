export const metadata = {
  title: 'Redirecting...',
  refresh: {
    httpEquiv: 'refresh',
    content: '0;url=/login',
  },
};

export default function Home() {
  return (
    <>
      <meta httpEquiv="refresh" content="0;url=/login" />
      <script dangerouslySetInnerHTML={{ __html: `window.location.replace('/login');` }} />
      <div className="flex items-center justify-center min-h-screen">
        Redirecting to login...
      </div>
    </>
  );
}

