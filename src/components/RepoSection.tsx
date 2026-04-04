"use client";

import { AgentFramework, SOURCES, TrendingRepo } from "@/lib/types";
import TabGroup from "./TabGroup";
import VizSource from "./VizSource";

interface RepoSectionProps {
  daily: TrendingRepo[];
  weekly: TrendingRepo[];
  monthly: TrendingRepo[];
  frameworks: AgentFramework[];
}

const REPO_TABS = [
  { key: "daily", label: "Today" },
  { key: "weekly", label: "This Week" },
  { key: "monthly", label: "This Month" },
];

const FRAMEWORK_TABS = [
  { key: "momentum", label: "Momentum (28D)" },
  { key: "scale", label: "Scale (Total Stars)" },
];

function RepoCard({ repo }: { repo: TrendingRepo }) {
  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
      <span className="flex-shrink-0 w-6 text-center font-mono text-sm text-gray-400">
        {repo.rank}
      </span>
      <div className="flex-1 min-w-0">
        <a
          href={repo.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-semibold text-gray-900 dark:text-gray-100 hover:underline"
        >
          {repo.name}
        </a>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">
          {repo.description}
        </p>
        <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-400 dark:text-gray-500">
          <span className="flex items-center gap-1">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: repo.language_color }}
            />
            {repo.language}
          </span>
          <span>★ {repo.stars.toLocaleString()}</span>
          <span className="text-green-600 dark:text-green-400 font-medium">
            +{repo.stars_delta.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
}

function FrameworkCard({ framework }: { framework: AgentFramework }) {
  return (
    <div className="flex items-start gap-3 border-b border-slate-100 py-3 last:border-b-0 dark:border-slate-800">
      <span className="w-6 flex-shrink-0 text-center font-mono text-sm text-slate-400">
        {framework.rank}
      </span>
      <div className="min-w-0 flex-1">
        <a
          href={framework.url}
          target="_blank"
          rel="noopener noreferrer"
          className="block truncate text-sm font-semibold text-slate-900 hover:underline dark:text-slate-100"
        >
          {framework.name}
        </a>
        <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
          {framework.description ?? "Open-source agent framework for building LLM applications."}
        </p>
        <div className="mt-1.5 flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span className="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {framework.category ?? "Agent Framework"}
          </span>
          <span className="flex items-center gap-1">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: framework.language_color ?? "#94a3b8" }}
            />
            {framework.language ?? "Unknown"}
          </span>
          <span>★ {framework.total_stars.toLocaleString()}</span>
          <span className="font-medium text-emerald-600 dark:text-emerald-400">
            +{framework.stars_28d.toLocaleString()} / 28d
          </span>
        </div>
      </div>
    </div>
  );
}

export default function RepoSection({
  daily,
  weekly,
  monthly,
  frameworks,
}: RepoSectionProps) {
  const dataMap: Record<string, TrendingRepo[]> = { daily, weekly, monthly };
  const rankedByMomentum = [...frameworks]
    .sort((a, b) => b.stars_28d - a.stars_28d)
    .map((framework, index) => ({ ...framework, rank: index + 1 }));
  const rankedByScale = [...frameworks]
    .sort((a, b) => b.total_stars - a.total_stars)
    .map((framework, index) => ({ ...framework, rank: index + 1 }));
  const frameworkMap: Record<string, AgentFramework[]> = {
    momentum: rankedByMomentum,
    scale: rankedByScale,
  };

  return (
    <section id="repos" className="mb-10">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Builder Signals</h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Track what developers ship now and which agent frameworks are absorbing the fastest
          community adoption.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white/85 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              GitHub Trending Projects
            </h3>
            <VizSource source={SOURCES.github_trending} />
          </div>

          <TabGroup tabs={REPO_TABS}>
            {(activeTab) => (
              <div>
                {(dataMap[activeTab] ?? []).map((repo) => (
                  <RepoCard key={repo.name} repo={repo} />
                ))}
              </div>
            )}
          </TabGroup>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white/85 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              Agent Framework Ranking
            </h3>
            <VizSource source={SOURCES.ossinsight_frameworks} />
          </div>
          <TabGroup tabs={FRAMEWORK_TABS}>
            {(activeTab) => (
              <>
                <div>
                  {(frameworkMap[activeTab] ?? []).map((framework) => (
                    <FrameworkCard key={framework.name} framework={framework} />
                  ))}
                </div>
              </>
            )}
          </TabGroup>
        </div>
      </div>
    </section>
  );
}
