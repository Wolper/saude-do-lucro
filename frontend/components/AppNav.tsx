"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { removeToken } from "../lib/api";

const navItems = [
  { href: "/app", label: "Início" },
  { href: "/app/entries", label: "Receitas e despesas" },
  { href: "/app/business-costs", label: "Custos fixos" },
];

export function AppNav() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    removeToken();
    router.push("/login");
  }

  return (
    <nav className="rounded-3xl border border-white/10 bg-white/[0.06] p-3 shadow-2xl shadow-emerald-950/20">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="grid gap-2 sm:flex sm:flex-wrap">
          {navItems.map((item) => {
            const isActive = pathname === item.href;

            return (
              <Link
                aria-current={isActive ? "page" : undefined}
                className={`rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                  isActive
                    ? "bg-emerald-400 text-slate-950"
                    : "text-slate-200 hover:bg-white/10 hover:text-white"
                }`}
                href={item.href}
                key={item.href}
              >
                {item.label}
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
