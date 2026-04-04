// ---- Models ----

export interface TrendingModel {
  rank: number;
  name: string;
  org: string;
  trending_score: number;
  downloads: number;
  likes: number;
  url: string;
  tags: string[];
  rank_change: number | null; // positive = up, negative = down, null = new
}

export interface BenchmarkModel {
  rank: number;
  name: string;
  org: string;
  intelligence_index: number;
  price_input: number | null;
  price_output: number | null;
  speed_tps: number | null;
  context_window: number | null;
  url: string;
}

// ---- Agents ----

export interface AgentEntry {
  rank: number;
  name: string;
  org: string;
  score: number;
  score_unit: string; // e.g. "%", "pass@1"
  url: string;
  verified: boolean;
}

// ---- GitHub Repos ----

export interface TrendingRepo {
  rank: number;
  name: string; // "owner/repo"
  description: string;
  url: string;
  stars: number;
  stars_delta: number; // stars gained in the time window
  language: string;
  language_color: string;
}

export interface AgentFramework {
  rank: number;
  name: string; // "owner/repo"
  url: string;
  stars_28d: number;
  total_stars: number;
  description?: string;
  category?: string;
  language?: string;
  language_color?: string;
}

// ---- Papers ----

export interface Paper {
  rank: number;
  title: string;
  authors: string[]; // first 3 authors
  url: string;
  categories: string[]; // e.g. ["cs.CL", "cs.AI"]
  upvotes: number | null;
  published: string; // ISO date
}

// ---- Dashboard (top-level) ----

export interface DashboardData {
  generated: string; // ISO timestamp
  models: {
    trending: TrendingModel[];
    benchmark: BenchmarkModel[];
  };
  agents: {
    general: AgentEntry[];
    coding: AgentEntry[];
    tool_use: AgentEntry[];
  };
  repos: {
    daily: TrendingRepo[];
    weekly: TrendingRepo[];
    monthly: TrendingRepo[];
    frameworks: AgentFramework[];
  };
  papers: {
    hf_trending: Paper[];
    arxiv_recent: Paper[];
  };
}

// ---- Source metadata ----

export interface SourceInfo {
  name: string;
  url: string;
  update_frequency: "hourly" | "daily";
}

export const SOURCES: Record<string, SourceInfo> = {
  hf_models: {
    name: "Hugging Face",
    url: "https://huggingface.co/models?sort=trending",
    update_frequency: "hourly",
  },
  artificial_analysis: {
    name: "Artificial Analysis",
    url: "https://artificialanalysis.ai/leaderboards/models",
    update_frequency: "daily",
  },
  gaia: {
    name: "GAIA Benchmark",
    url: "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
    update_frequency: "daily",
  },
  swebench: {
    name: "SWE-bench",
    url: "https://www.swebench.com/",
    update_frequency: "daily",
  },
  bfcl: {
    name: "BFCL",
    url: "https://gorilla.cs.berkeley.edu/leaderboard.html",
    update_frequency: "daily",
  },
  github_trending: {
    name: "GitHub Trending",
    url: "https://github.com/trending",
    update_frequency: "hourly",
  },
  ossinsight_frameworks: {
    name: "OSSInsight Agent Frameworks",
    url: "https://ossinsight.io/collections/ai-agent-frameworks",
    update_frequency: "daily",
  },
  arxiv: {
    name: "arXiv",
    url: "https://arxiv.org/list/cs.AI/recent",
    update_frequency: "hourly",
  },
  hf_papers: {
    name: "Hugging Face Papers",
    url: "https://huggingface.co/papers",
    update_frequency: "hourly",
  },
};
