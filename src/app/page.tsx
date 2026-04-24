import { getDashboardData } from "@/lib/data";
import DashboardHeader from "@/components/DashboardHeader";
import ModelSection from "@/components/ModelSection";
import RepoSection from "@/components/RepoSection";
import PaperSection from "@/components/PaperSection";
import HackerNewsSection from "@/components/HackerNewsSection";
import PersonaGuide from "@/components/PersonaGuide";
import { AgentFramework, TrendingRepo } from "@/lib/types";

export default function Home() {
  const data = getDashboardData();
  const breakoutRepo =
    data.repos.daily.reduce<TrendingRepo | null>((best, repo) => {
      if (!best || repo.stars_delta > best.stars_delta) return repo;
      return best;
    }, null) ?? null;
  const topModel = data.models.benchmark[0] ?? null;
  const topFramework =
    (data.repos.frameworks ?? []).reduce<AgentFramework | null>((best, framework) => {
      if (!best || framework.stars_28d > best.stars_28d) return framework;
      return best;
    }, null) ?? null;

  return (
    <>
      <DashboardHeader
        generated={data.generated}
        breakoutRepo={breakoutRepo}
        topModel={topModel}
        topFramework={topFramework}
      />
      <PersonaGuide />
      <ModelSection
        trending={data.models.trending}
        benchmark={data.models.benchmark}
        general={data.agents.general}
        coding={data.agents.coding}
        tool_use={data.agents.tool_use}
      />
      <PaperSection
        hf_trending={data.papers.hf_trending}
        arxiv_recent={data.papers.arxiv_recent}
      />
      <HackerNewsSection
        top={data.hn?.top ?? []}
        ask={data.hn?.ask ?? []}
        show={data.hn?.show ?? []}
      />
      <RepoSection
        daily={data.repos.daily}
        weekly={data.repos.weekly}
        monthly={data.repos.monthly}
        frameworks={data.repos.frameworks ?? []}
      />
    </>
  );
}
