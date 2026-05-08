"use client";

import {
  AgentEntry,
  BenchmarkModel,
  SourceInfo,
  SOURCES,
  TrendingModel,
} from "@/lib/types";
import { rankChangeLabel, rankChangeColor } from "@/lib/format";
import RankTable from "./RankTable";
import VizSource from "./VizSource";
import TabGroup from "./TabGroup";

interface ModelSectionProps {
  trending: TrendingModel[];
  benchmark: BenchmarkModel[];
  general: AgentEntry[];
  coding: AgentEntry[];
  tool_use: AgentEntry[];
}

const MODEL_CORE_TABS = [
  { key: "trending", label: "Trending (HF)" },
  { key: "benchmark", label: "Benchmark (AA)" },
];

const MODEL_CORE_META: Record<string, { source: SourceInfo; note: string }> = {
  trending: {
    source: SOURCES.hf_models,
    note: "HF community momentum.",
  },
  benchmark: {
    source: SOURCES.artificial_analysis,
    note: "Capability and cost-performance comparison on standardized evals.",
  },
};

const AGENT_MODEL_TABS = [
  { key: "general", label: "General (GAIA)" },
  { key: "coding", label: "Coding (SWE-bench)" },
  { key: "tool_use", label: "Tool-Use (BFCL)" },
];

const AGENT_MODEL_META: Record<string, { source: SourceInfo; note: string }> = {
  general: {
    source: SOURCES.gaia,
    note: "General autonomy and reasoning across realistic tasks.",
  },
  coding: {
    source: SOURCES.swebench,
    note: "Code issue resolution with model + orchestration pipelines.",
  },
  tool_use: {
    source: SOURCES.bfcl,
    note: "Function/tool-call accuracy of model-driven systems.",
  },
};

const agentColumns = [
  {
    header: "#",
    className: "w-8 text-center",
    render: (a: AgentEntry) => <span className="font-mono text-gray-400">{a.rank}</span>,
  },
  {
    header: "System",
    render: (a: AgentEntry) => (
      <div>
        <a
          href={a.url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-slate-900 hover:underline dark:text-slate-100"
        >
          {a.name}
        </a>
        <div className="text-xs text-slate-400 dark:text-slate-500">{a.org}</div>
      </div>
    ),
  },
  {
    header: "Score",
    className: "w-24 text-right",
    render: (a: AgentEntry) => (
      <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
        {a.score}
        <span className="ml-1 text-xs text-gray-400 dark:text-gray-500">{a.score_unit}</span>
      </span>
    ),
  },
  {
    header: "",
    className: "w-8",
    render: (a: AgentEntry) =>
      a.verified ? (
        <span className="text-xs text-green-600 dark:text-green-400" title="Verified">
          ✓
        </span>
      ) : null,
  },
];

function CodingCard({ entry, maxScore }: { entry: AgentEntry; maxScore: number }) {
  const barPct = maxScore > 0 ? (entry.score / maxScore) * 100 : 0;
  const costColor =
    entry.cost_per_bug == null
      ? ""
      : entry.cost_per_bug < 0.2
      ? "text-emerald-600 dark:text-emerald-400"
      : entry.cost_per_bug < 0.6
      ? "text-amber-600 dark:text-amber-400"
      : "text-rose-500 dark:text-rose-400";

  return (
    <div className="py-3 border-b border-slate-100 dark:border-slate-800 last:border-b-0">
      <div className="flex items-start gap-3">
        <span className="w-6 flex-shrink-0 text-center font-mono text-sm text-slate-400 pt-0.5">
          {entry.rank}
        </span>
        <div className="flex-1 min-w-0">
          {/* Name + score */}
          <div className="flex items-baseline justify-between gap-2">
            <a
              href={entry.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-semibold text-slate-900 dark:text-slate-100 hover:underline leading-snug truncate"
            >
              {entry.name}
            </a>
            <span className="flex-shrink-0 font-mono text-sm font-bold text-blue-600 dark:text-blue-400">
              {entry.score}%
            </span>
          </div>

          {/* Bar */}
          <div className="mt-1.5 h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-blue-500 dark:bg-blue-400 transition-all"
              style={{ width: `${barPct}%` }}
            />
          </div>

          {/* Org + cost metrics */}
          <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-0.5 text-xs">
            <span className="text-slate-400 dark:text-slate-500">{entry.org}</span>
            {entry.avg_cost_usd != null && (
              <span className="text-slate-500 dark:text-slate-400">
                ${entry.avg_cost_usd.toFixed(2)}/task
              </span>
            )}
            {entry.cost_per_bug != null && (
              <span className={`font-semibold ${costColor}`} title="Average cost per bug resolved">
                ${entry.cost_per_bug.toFixed(2)}/bug fixed
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const trendingColumns = [
  {
    header: "#",
    className: "w-8 text-center",
    render: (m: TrendingModel) => <span className="font-mono text-gray-400">{m.rank}</span>,
  },
  {
    header: "Model",
    render: (m: TrendingModel) => (
      <div>
        <a
          href={m.url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-slate-900 hover:underline dark:text-slate-100"
        >
          {m.name.split("/").pop()}
        </a>
        <div className="text-xs text-slate-400 dark:text-slate-500">{m.org}</div>
      </div>
    ),
  },
  {
    header: "Score",
    className: "text-right w-16",
    render: (m: TrendingModel) => (
      <span className="font-mono text-gray-700 dark:text-gray-300">{m.trending_score}</span>
    ),
  },
  {
    header: "",
    className: "w-12 text-right",
    render: (m: TrendingModel) => (
      <span className={`text-xs font-medium ${rankChangeColor(m.rank_change)}`}>
        {rankChangeLabel(m.rank_change)}
      </span>
    ),
  },
];

const benchmarkColumns = [
  {
    header: "#",
    className: "w-8 text-center",
    render: (m: BenchmarkModel) => <span className="font-mono text-gray-400">{m.rank}</span>,
  },
  {
    header: "Model",
    render: (m: BenchmarkModel) => (
      <div>
        <a
          href={m.url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-slate-900 hover:underline dark:text-slate-100"
        >
          {m.name}
        </a>
        <div className="text-xs text-slate-400 dark:text-slate-500">{m.org}</div>
      </div>
    ),
  },
  {
    header: "Index",
    className: "text-right w-14",
    render: (m: BenchmarkModel) => (
      <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
        {m.intelligence_index}
      </span>
    ),
  },
  {
    header: "$/M in",
    className: "text-right w-16",
    render: (m: BenchmarkModel) => (
      <span className="font-mono text-xs text-gray-500 dark:text-gray-400">
        {m.price_input !== null ? `$${m.price_input}` : "—"}
      </span>
    ),
  },
  {
    header: "Ctx",
    className: "text-right w-16 hidden sm:table-cell",
    render: (m: BenchmarkModel) => (
      <span className="font-mono text-xs text-gray-500 dark:text-gray-400">
        {m.context_window !== null ? `${Math.round(m.context_window / 1000)}k` : "—"}
      </span>
    ),
  },
];

export default function ModelSection({
  trending,
  benchmark,
  general,
  coding,
  tool_use,
}: ModelSectionProps) {
  const coreDataMap: Record<string, TrendingModel[] | BenchmarkModel[]> = {
    trending,
    benchmark,
  };
  const agentDataMap: Record<string, AgentEntry[]> = { general, coding, tool_use };

  return (
    <section id="models" className="mb-10">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
          Model Intelligence
        </h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Track core model frontier and model-powered agentic performance in parallel.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div
          id="models-core"
          className="rounded-2xl border border-slate-200 bg-white/85 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/70"
        >
          <div className="mb-3 flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              Core Models
            </h3>
          </div>

          <TabGroup tabs={MODEL_CORE_TABS}>
            {(activeTab) => {
              const meta = MODEL_CORE_META[activeTab];

              return (
                <>
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                      {meta.note}
                    </p>
                    <VizSource source={meta.source} />
                  </div>
                  {activeTab === "benchmark" ? (
                    <RankTable
                      data={coreDataMap[activeTab] as BenchmarkModel[]}
                      columns={benchmarkColumns}
                    />
                  ) : (
                    <RankTable
                      data={coreDataMap[activeTab] as TrendingModel[]}
                      columns={trendingColumns}
                    />
                  )}
                </>
              );
            }}
          </TabGroup>
        </div>

        <div
          id="models-agentic"
          className="rounded-2xl border border-slate-200 bg-white/85 p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900/70"
        >
          <div className="mb-3">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
              Agentic Benchmarks
            </h3>
          </div>

          <TabGroup tabs={AGENT_MODEL_TABS}>
            {(activeTab) => {
              const meta = AGENT_MODEL_META[activeTab];
              const entries = agentDataMap[activeTab] ?? [];
              return (
                <>
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                    <p className="text-xs text-slate-500 dark:text-slate-400">{meta.note}</p>
                    <VizSource source={meta.source} />
                  </div>
                  {activeTab === "coding" ? (
                    <>
                      <div className="mb-2 flex justify-end gap-4 text-[10px] font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
                        <span>resolve %</span>
                        <span className="text-emerald-600 dark:text-emerald-500">&lt;$0.20</span>
                        <span className="text-amber-600 dark:text-amber-500">$0.20–0.60</span>
                        <span className="text-rose-500 dark:text-rose-400">&gt;$0.60 / bug</span>
                      </div>
                      <div>
                        {entries.map((entry) => (
                          <CodingCard
                            key={entry.name}
                            entry={entry}
                            maxScore={entries[0]?.score ?? 100}
                          />
                        ))}
                      </div>
                      <p className="mt-2 text-[10px] text-slate-400 dark:text-slate-500">
                        Standardized with mini-SWE-agent v2 · SWE-bench Verified (500 instances)
                      </p>
                    </>
                  ) : (
                    <RankTable data={entries} columns={agentColumns} />
                  )}
                </>
              );
            }}
          </TabGroup>
        </div>
      </div>
    </section>
  );
}
