"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  Company,
  User,
  getCurrentCompany,
  getCurrentUser,
  readToken,
  removeToken,
} from "../../lib/api";

export default function AppPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = readToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    const authToken = token;

    async function loadAccount() {
      try {
        const [currentUser, currentCompany] = await Promise.all([
          getCurrentUser(authToken),
          getCurrentCompany(authToken),
        ]);
        setUser(currentUser);
        setCompany(currentCompany);
      } catch {
        removeToken();
        setError("Sua sessão expirou. Entre novamente.");
        router.replace("/login");
      } finally {
        setIsLoading(false);
      }
    }

    loadAccount();
  }, [router]);

  function handleLogout() {
    removeToken();
    router.push("/login");
  }

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
        <p className="text-sm text-slate-300">Carregando sua conta...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6">
      <section className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        <header className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/[0.06] p-6 shadow-2xl shadow-emerald-950/25 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">
              Saúde do Lucro
            </p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight">Área inicial</h1>
          </div>
          <button
            className="rounded-2xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:border-emerald-300 hover:text-emerald-200"
            onClick={handleLogout}
            type="button"
          >
            Sair
          </button>
        </header>

        {error ? (
          <p className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <p className="text-sm text-slate-300">Olá,</p>
          <h2 className="mt-1 text-2xl font-bold text-white">{user?.name}</h2>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-slate-950/60 p-4">
              <p className="text-sm text-slate-400">Empresa</p>
              <p className="mt-1 text-lg font-semibold text-emerald-100">{company?.name}</p>
            </div>
            <div className="rounded-2xl bg-slate-950/60 p-4">
              <p className="text-sm text-slate-400">Segmento</p>
              <p className="mt-1 text-lg font-semibold text-emerald-100">{company?.segment}</p>
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-emerald-300/20 bg-emerald-300/10 p-6">
          <p className="text-lg font-semibold text-emerald-50">
            Base da conta criada. Próximo passo: cadastrar lançamentos financeiros.
          </p>
          <p className="mt-3 text-sm leading-6 text-emerald-100/80">
            O dashboard financeiro ainda não foi implementado. Esta tela confirma apenas que sua
            conta e empresa estão conectadas.
          </p>
        </section>
      </section>
    </main>
  );
}
