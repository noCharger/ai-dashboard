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
              return (
                <>
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                    <p className="text-xs text-slate-500 dark:text-slate-400">{meta.note}</p>
                    <VizSource source={meta.source} />
                  </div>
                  <RankTable data={agentDataMap[activeTab] ?? []} columns={agentColumns} />
                </>
              );
            }}
          </TabGroup>
        </div>
      </div>
    </section>
  );
}
