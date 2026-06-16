"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { removeToken } from "../lib/api";

const navLinks = [
  { href: "/app", label: "Início" },
  { href: "/app/entries", label: "Receitas e despesas" },
  { href: "/app/business-costs", label: "Custos fixos" },
];

export default function AppNav() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    removeToken();
    router.push("/login");
  }

  return (
    <nav className="rounded-3xl border border-white/10 bg-white/[0.06] p-3 shadow-2xl shadow-emerald-950/20">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="grid gap-2 sm:flex sm:flex-wrap">
          {navLinks.map((link) => {
            const isCurrent = pathname === link.href;

            return (
              <Link
                aria-current={isCurrent ? "page" : undefined}
                className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                  isCurrent
                    ? "bg-emerald-400 text-slate-950"
                    : "text-slate-200 hover:bg-white/10 hover:text-white"
                }`}
                href={link.href}
                key={link.href}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
        <button
          className="rounded-2xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-emerald-300 hover:text-emerald-200"
          onClick={handleLogout}
          type="button"
        >
          Sair
        </button>
      </div>
    </nav>
  );
}
