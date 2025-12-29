export function formatDate(dateString: string): string {
  // Extract date part to avoid timezone conversion issues
  // published_at format: "2025-12-23T00:00:00.000+09:00"
  const datePart = dateString.substring(0, 10); // "2025-12-23"
  const [year, month, day] = datePart.split('-');

  // Create date without timezone conversion
  const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };
  return date.toLocaleDateString('en-US', options);
}

export function formatRelativeTime(dateString: string): string {
  // Parse the full ISO timestamp with timezone: "2025-12-23T09:50:06.000+09:00"
  const date = new Date(dateString);
  const now = new Date();

  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 60) {
    return diffMins <= 1 ? 'Just now' : `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return formatDate(dateString);
  }
}
