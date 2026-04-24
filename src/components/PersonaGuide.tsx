"use client";

import { useMemo, useState } from "react";

interface PersonaPlan {
  key: string;
  label: string;
  hook: string;
  description: string;
  steps: { href: string; label: string }[];
}

const PERSONAS: PersonaPlan[] = [
  {
    key: "builder",
    label: "Builder / Dev",
    hook: "Want to ship faster this week",
    description:
      "Start from agent capability, then pressure-test demand and implementation pull from community discussion and repo momentum.",
    steps: [
      { href: "#models-agentic", label: "Inspect agentic benchmark strength" },
      { href: "#hn", label: "Scan Hacker News for live operator demand" },
      { href: "#repos", label: "Track GitHub momentum for implementation stacks" },
    ],
  },
  {
    key: "researcher",
    label: "Researcher",
    hook: "Need frontier direction and evidence",
    description:
      "Begin with model frontier shifts, then follow papers and community discussion to see which ideas are crossing into broader attention.",
    steps: [
      { href: "#models", label: "Read the current model frontier" },
      { href: "#papers", label: "Scan papers driving new techniques" },
      { href: "#hn", label: "See which concepts are escaping the lab" },
    ],
  },
  {
    key: "strategist",
    label: "Product / Investor",
    hook: "Looking for asymmetric opportunities",
    description:
      "Use the breakout signal first, then cross-check discussion intensity and developer adoption before deciding bets.",
    steps: [
      { href: "#breakout", label: "Start from today's breakout signal" },
      { href: "#hn", label: "Check what the market is debating right now" },
      { href: "#repos", label: "Confirm market pull through open-source velocity" },
    ],
  },
];

export default function PersonaGuide() {
  const [active, setActive] = useState(PERSONAS[0].key);
  const persona = useMemo(
    () => PERSONAS.find((item) => item.key === active) ?? PERSONAS[0],
    [active]
  );

  return (
    <section className="mb-10 rounded-2xl border border-slate-200 bg-white/85 p-5 shadow-sm backdrop-blur dark:border-slate-700 dark:bg-slate-900/70">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700 dark:text-cyan-300">
            Persona Paths
          </p>
          <h2 className="mt-1 text-xl font-semibold text-slate-900 dark:text-slate-100">
            Choose Your Lens
          </h2>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Different audience, different order. Pick one path and follow it in under five minutes.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {PERSONAS.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setActive(item.key)}
              className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                item.key === active
                  ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900/80">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          {persona.hook}
        </p>
        <p className="mt-2 text-sm text-slate-700 dark:text-slate-200">{persona.description}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {persona.steps.map((step, index) => (
            <a
              key={step.href}
              href={step.href}
              className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:border-slate-300 hover:text-slate-950 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300 dark:hover:border-slate-500 dark:hover:text-slate-100"
            >
              {index + 1}. {step.label}
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
