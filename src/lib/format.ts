export function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  });
}

export function rankChangeLabel(change: number | null): string {
  if (change === null) return "NEW";
  if (change > 0) return `▲${change}`;
  if (change < 0) return `▼${Math.abs(change)}`;
  return "—";
}

export function rankChangeColor(change: number | null): string {
  if (change === null) return "text-blue-500 dark:text-blue-400";
  if (change > 0) return "text-green-600 dark:text-green-400";
  if (change < 0) return "text-red-500 dark:text-red-400";
  return "text-gray-400 dark:text-gray-500";
}
