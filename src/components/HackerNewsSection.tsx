"use client";

import { HnStory, SourceInfo, SOURCES } from "@/lib/types";
import TabGroup from "./TabGroup";
import VizSource from "./VizSource";

interface HackerNewsSectionProps {
  top: HnStory[];
  ask: HnStory[];
  show: HnStory[];
}

const HN_TABS = [
  { key: "top", label: "Top" },
  { key: "ask", label: "Ask HN" },
  { key: "show", label: "Show HN" },
];

const HN_META: Record<string, { source: SourceInfo; note: string }> = {
  top: {
    source: SOURCES.hacker_news,
    note: "The broader tech crowd's live attention market.",
  },
  ask: {
    source: SOURCES.hacker_news,
    note: "Operator pain points, buying intent, and practical questions surfacing in public.",
  },
  show: {
    source: SOURCES.hacker_news,
    note: "Fresh demos, indie launches, and tools being put in front of real peers.",
  },
};

function HnStoryRow({ story }: { story: HnStory }) {
  const titleHref = story.url?.trim() || story.discussion_url;
  const hasSeparateDiscussion = Boolean(story.url && story.url !== story.discussion_url);
  const siteLabel = story.site === "news.ycombinator.com" ? "HN" : story.site;

  return (
    <div className="border-b border-slate-100 py-3 last:border-b-0 dark:border-slate-800">
      <div className="flex items-start gap-3">
        <span className="w-6 flex-shrink-0 text-center font-mono text-sm text-slate-400">
          {story.rank}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start gap-x-3 gap-y-1">
            <a
              href={titleHref}
              target="_blank"
              rel="noopener noreferrer"
              className="min-w-0 flex-1 text-sm font-semibold leading-snug text-slate-900 hover:underline dark:text-slate-100"
            >
              {story.title}
            </a>
            {hasSeparateDiscussion && (
              <a
                href={story.discussion_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex rounded-full border border-orange-200 bg-orange-50 px-2 py-0.5 text-[11px] font-medium text-orange-700 transition-colors hover:border-orange-300 hover:bg-orange-100 dark:border-orange-500/30 dark:bg-orange-500/10 dark:text-orange-300 dark:hover:border-orange-400/40"
              >
                Discuss
              </a>
            )}
          </div>

          <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
            <span className="inline-flex rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {siteLabel}
            </span>
            <span className="font-medium text-orange-600 dark:text-orange-400">
              ▲ {story.points}
            </span>
            <span>{story.comments} comments</span>
            <span>by {story.author}</span>
            {story.age && <span>{story.age}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HackerNewsSection({ top, ask, show }: HackerNewsSectionProps) {
  const dataMap: Record<string, HnStory[]> = { top, ask, show };

  return (
    <section id="hn" className="mb-10">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
          Community Pulse
        </h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          See what the broader builder and operator crowd is discussing before it hardens into
          consensus.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white/85 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
        <TabGroup tabs={HN_TABS}>
          {(activeTab) => {
            const stories = dataMap[activeTab] ?? [];
            const meta = HN_META[activeTab];

            return (
              <>
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                  <p className="text-xs text-slate-500 dark:text-slate-400">{meta.note}</p>
                  <VizSource source={meta.source} />
                </div>
                {stories.length > 0 ? (
                  <div>
                    {stories.map((story) => (
                      <HnStoryRow key={story.id} story={story} />
                    ))}
                  </div>
                ) : (
                  <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-400">
                    No Hacker News stories were captured in this snapshot.
                  </div>
                )}
              </>
            );
          }}
        </TabGroup>
      </div>
    </section>
  );
}
