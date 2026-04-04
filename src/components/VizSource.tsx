import { SourceInfo } from "@/lib/types";

interface VizSourceProps {
  source: SourceInfo;
}

export default function VizSource({ source }: VizSourceProps) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white/80 px-2.5 py-1 text-[11px] font-medium text-slate-600 transition-colors hover:border-slate-300 hover:text-slate-900 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-300 dark:hover:border-slate-500 dark:hover:text-slate-100"
    >
      Source
      <span className="text-slate-400 dark:text-slate-500">·</span>
      {source.name}
    </a>
  );
}
