import { formatTimestamp } from "@/lib/format";
import { AgentFramework, BenchmarkModel, TrendingRepo } from "@/lib/types";
import FollowCTA from "./FollowCTA";

interface DashboardHeaderProps {
  generated: string;
  breakoutRepo: TrendingRepo | null;
  topModel: BenchmarkModel | null;
  topFramework: AgentFramework | null;
}

export default function DashboardHeader({
  generated,
  breakoutRepo,
  topModel,
  topFramework,
}: DashboardHeaderProps) {
  return (
    <header id="breakout" className="mb-10">
      <div className="rounded-3xl border border-slate-200 bg-gradient-to-br from-amber-50 via-white to-cyan-50 p-5 shadow-sm sm:p-7 dark:border-slate-700 dark:from-slate-900 dark:via-slate-950 dark:to-cyan-950/40">
        <div className="grid gap-5 xl:grid-cols-[1.45fr_0.9fr]">
          <div className="rounded-2xl border border-slate-200/80 bg-white/75 p-5 dark:border-slate-700 dark:bg-slate-900/55">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-700 dark:text-amber-300">
              Daily AI Signal Radar
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl dark:text-slate-100">
              Catch AI Breakouts Before They Become Headlines
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-700 sm:text-base dark:text-slate-200">
              A personal daily brief that combines model frontier changes, builder momentum, and
              research direction into one narrative.
            </p>
            <p className="mt-4 inline-flex rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-300">
              Last updated: {formatTimestamp(generated)}
            </p>
          </div>
          <FollowCTA />
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-3">
          {breakoutRepo && (
            <a
              href={breakoutRepo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-2xl border border-rose-200 bg-rose-50/80 p-4 transition-colors hover:border-rose-300 hover:bg-rose-50 dark:border-rose-500/30 dark:bg-rose-500/10 dark:hover:border-rose-400/40"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-rose-700 dark:text-rose-300">
                Breakout Signal
              </p>
              <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
                {breakoutRepo.name}
              </p>
              <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
                +{breakoutRepo.stars_delta.toLocaleString()} stars in 24h.
              </p>
            </a>
          )}

          {topModel && (
            <a
              href={topModel.url}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-2xl border border-slate-200 bg-white/80 p-4 transition-colors hover:border-slate-300 dark:border-slate-700 dark:bg-slate-900/70 dark:hover:border-slate-500"
            >
              <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                #1 Model Frontier
              </p>
              <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
                {topModel.name}
              </p>
              <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
                Intelligence Index {topModel.intelligence_index}
              </p>
            </a>
          )}

          {topFramework && (
            <a
              href={topFramework.url}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-2xl border border-slate-200 bg-white/80 p-4 transition-colors hover:border-slate-300 dark:border-slate-700 dark:bg-slate-900/70 dark:hover:border-slate-500"
            >
              <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
                #1 OSS Agent Framework
              </p>
              <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
                {topFramework.name}
              </p>
              <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
                +{topFramework.stars_28d.toLocaleString()} stars in 28d.
              </p>
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
