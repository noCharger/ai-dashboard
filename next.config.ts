import type { NextConfig } from "next";

function normalizeBasePath(value: string): string {
  if (!value || value === "/") return "";
  return value.startsWith("/") ? value : `/${value}`;
}

const explicitBasePath = normalizeBasePath(process.env.PAGES_BASE_PATH ?? "");
const [repoOwner = "", repoName = ""] = (process.env.GITHUB_REPOSITORY ?? "").split("/");
const inferredBasePath =
  process.env.GITHUB_ACTIONS === "true" &&
  repoOwner &&
  repoName &&
  repoName !== `${repoOwner}.github.io`
    ? `/${repoName}`
    : "";
const normalizedBasePath = explicitBasePath || inferredBasePath;

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  ...(normalizedBasePath
    ? {
        basePath: normalizedBasePath,
        assetPrefix: normalizedBasePath,
      }
    : {}),
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "github.com" },
      { protocol: "https", hostname: "avatars.githubusercontent.com" },
    ],
  },
};

export default nextConfig;
