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
