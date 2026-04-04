import { CREATOR_PROFILE } from "@/lib/profile";

export default function FollowCTA() {
  const profileLink = CREATOR_PROFILE.links[0]?.href ?? `https://github.com/${CREATOR_PROFILE.username}`;
  const followButtonSrc = `https://ghbtns.com/github-btn.html?user=${encodeURIComponent(
    CREATOR_PROFILE.username
  )}&type=follow&count=true&size=large`;

  return (
    <aside className="rounded-2xl border border-amber-200/80 bg-amber-50/85 p-5 shadow-sm backdrop-blur dark:border-amber-500/30 dark:bg-amber-500/10">
      <div className="flex items-center gap-3">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={CREATOR_PROFILE.avatar}
          alt={`${CREATOR_PROFILE.name} avatar`}
          className="h-14 w-14 rounded-full border border-amber-200 object-cover shadow-sm dark:border-amber-400/40"
        />
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700 dark:text-amber-300">
            Follow The Curator
          </p>
          <h2 className="mt-1 text-xl font-semibold text-slate-900 dark:text-slate-100">
            <a href={profileLink} target="_blank" rel="noopener noreferrer" className="hover:underline">
              {CREATOR_PROFILE.name}
            </a>
          </h2>
        </div>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-slate-700 dark:text-slate-200">
        {CREATOR_PROFILE.bio}
      </p>

      <div className="mt-4">
        <iframe
          src={followButtonSrc}
          title={`Follow ${CREATOR_PROFILE.username} on GitHub`}
          width="240"
          height="32"
          className="max-w-full"
        />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {CREATOR_PROFILE.links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-slate-700 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-300"
          >
            {link.label}
          </a>
        ))}
      </div>
    </aside>
  );
}
