import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatTime(minutes) {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return `${hours}h ${mins}m`;
}

export function formatDistance(km) {
  return `${km.toFixed(1)} km`;
}

export function getTrafficColor(traffic) {
  const colors = {
    "Bajo": "#22c55e",
    "Medio": "#eab308",
    "Alto": "#f97316",
    "Muy Alto": "#ef4444"
  };
  return colors[traffic] || "#6b7280";
}

export function getAlgorithmBadgeColor(algo) {
  const colors = {
    "BFS": "bg-blue-500",
    "DFS": "bg-purple-500",
    "A*": "bg-emerald-500"
  };
  return colors[algo] || "bg-gray-500";
}