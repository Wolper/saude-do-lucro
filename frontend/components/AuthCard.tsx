import Link from "next/link";
import type { ReactNode } from "react";

type AuthCardProps = {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  footerText: string;
  footerHref: string;
  footerLinkLabel: string;
};

export function AuthCard({
  eyebrow,
  title,
  description,
  children,
  footerText,
  footerHref,
  footerLinkLabel,
}: AuthCardProps) {
  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6">
      <section className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-md flex-col justify-center">
        <Link className="mb-8 text-sm font-semibold text-emerald-300" href="/">
          Saúde do Lucro
        </Link>

        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6 shadow-2xl shadow-emerald-950/30 sm:p-8">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">
            {eyebrow}
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight">{title}</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">{description}</p>

          <div className="mt-8">{children}</div>
        </div>

        <p className="mt-6 text-center text-sm text-slate-300">
          {footerText}{" "}
          <Link className="font-semibold text-emerald-300 hover:text-emerald-200" href={footerHref}>
            {footerLinkLabel}
          </Link>
        </p>
      </section>
    </main>
  );
}
