"use client";

import { Paper, SourceInfo, SOURCES } from "@/lib/types";
import TabGroup from "./TabGroup";
import VizSource from "./VizSource";

interface PaperSectionProps {
  hf_trending: Paper[];
  arxiv_recent: Paper[];
}

const PAPER_TABS = [
  { key: "hf_trending", label: "HF Trending" },
  { key: "arxiv_recent", label: "arXiv Recent" },
];

const PAPER_META: Record<string, { source: SourceInfo; note: string }> = {
  hf_trending: {
    source: SOURCES.hf_papers,
    note: "Community-accelerated papers with strong early attention.",
  },
  arxiv_recent: {
    source: SOURCES.arxiv,
    note: "Fresh technical drops for first-look research tracking.",
  },
};

function PaperCard({ paper }: { paper: Paper }) {
  const authorsDisplay =
    paper.authors.length > 3
      ? paper.authors.slice(0, 3).join(", ") + " et al."
      : paper.authors.join(", ");

  return (
    <div className="py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
      <div className="flex items-start gap-3">
        <span className="flex-shrink-0 w-6 text-center font-mono text-sm text-gray-400">
          {paper.rank}
        </span>
        <div className="flex-1 min-w-0">
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-gray-900 dark:text-gray-100 hover:underline leading-snug"
          >
            {paper.title}
          </a>
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1 mt-1.5 text-xs text-gray-400 dark:text-gray-500">
            <span>{authorsDisplay}</span>
            <span>·</span>
            {paper.categories.map((cat) => (
              <span
                key={cat}
                className="inline-block px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs"
              >
                {cat}
              </span>
            ))}
            {paper.upvotes !== null && (
              <>
                <span>·</span>
                <span className="text-orange-500 dark:text-orange-400 font-medium">
                  ▲ {paper.upvotes}
                </span>
              </>
            )}
            <span>·</span>
            <span>{paper.published}</span>
            {paper.github_repo && (
              <>
                <span>·</span>
                <a
                  href={paper.github_repo}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:underline"
                >
                  <svg viewBox="0 0 16 16" className="w-3.5 h-3.5 fill-current flex-shrink-0" aria-hidden="true">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
                  </svg>
                  {paper.github_stars != null
                    ? `★ ${paper.github_stars >= 1000 ? (paper.github_stars / 1000).toFixed(1) + "k" : paper.github_stars}`
                    : "GitHub"}
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PaperSection({ hf_trending, arxiv_recent }: PaperSectionProps) {
  const dataMap: Record<string, Paper[]> = { hf_trending, arxiv_recent };

  return (
    <section id="papers" className="mb-10">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Research Feed</h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Move from leaderboard numbers to method-level insight and see which ideas are gathering
          real traction.
        </p>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white/85 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
        <TabGroup tabs={PAPER_TABS}>
          {(activeTab) => {
            const meta = PAPER_META[activeTab];
            return (
              <>
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                  <p className="text-xs text-slate-500 dark:text-slate-400">{meta?.note}</p>
                  {meta && <VizSource source={meta.source} />}
                </div>
                <div>
                  {(dataMap[activeTab] ?? []).map((paper) => (
                    <PaperCard key={paper.url} paper={paper} />
                  ))}
                </div>
              </>
            );
          }}
        </TabGroup>
      </div>
    </section>
  );
}
