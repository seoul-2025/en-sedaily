export function getImageUrl(publishedAt: string, originalLink: string): string {
  const date = publishedAt.substring(0, 10).split('-');
  const [year, month, day] = date;
  const code = originalLink.split('/').pop(); // Extract code from URL
  return `https://newsimg.sedaily.com/${year}/${month}/${day}/${code}_1.jpg`;
}
