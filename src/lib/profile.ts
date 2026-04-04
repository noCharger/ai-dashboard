interface CreatorLink {
  label: string;
  href: string;
}

const creatorId =
  (process.env.NEXT_PUBLIC_CREATOR_GITHUB_ID ?? "noCharger").replace(/^@/, "") || "noCharger";

export const CREATOR_PROFILE = {
  username: creatorId,
  name: process.env.NEXT_PUBLIC_CREATOR_NAME ?? creatorId,
  bio:
    process.env.NEXT_PUBLIC_CREATOR_BIO ??
    "Building in public around AI agents, model eval, and practical workflow systems.",
  avatar:
    process.env.NEXT_PUBLIC_CREATOR_AVATAR ??
    `https://avatars.githubusercontent.com/${creatorId}?size=200`,
  links: [
    {
      label: "GitHub Profile",
      href: process.env.NEXT_PUBLIC_CREATOR_GITHUB ?? `https://github.com/${creatorId}`,
    },
    {
      label: "Repositories",
      href: `https://github.com/${creatorId}?tab=repositories`,
    },
    {
      label: "Starred",
      href: `https://github.com/${creatorId}?tab=stars`,
    },
  ] satisfies CreatorLink[],
};
