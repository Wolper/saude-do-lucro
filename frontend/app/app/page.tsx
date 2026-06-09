"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type User = {
  name: string;
  email: string;
};

type Company = {
  name: string;
  segment: string;
  city?: string | null;
  state?: string | null;
};

export default function AppPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("saude_do_lucro_token");
    if (!token) {
      router.replace("/login");
      return;
    }

    async function loadAccount() {
      const headers = { Authorization: `Bearer ${token}` };
      const [userResponse, companyResponse] = await Promise.all([
        fetch(`${API_URL}/auth/me`, { headers }),
        fetch(`${API_URL}/companies/current`, { headers }),
      ]);

      if (!userResponse.ok || !companyResponse.ok) {
        localStorage.removeItem("saude_do_lucro_token");
        setError("Sessão inválida. Faça login novamente.");
        router.replace("/login");
        return;
      }

      setUser(await userResponse.json());
      setCompany(await companyResponse.json());
    }

    loadAccount().catch(() => {
      setError("Não foi possível carregar sua conta.");
    });
  }, [router]);

  function logout() {
    localStorage.removeItem("saude_do_lucro_token");
    router.push("/login");
  }

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-white">
      <section className="mx-auto max-w-2xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-emerald-950/20">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">
              Área protegida
            </p>
            <h1 className="mt-3 text-3xl font-bold">Saúde do Lucro</h1>
          </div>
          <button className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200" onClick={logout} type="button">
            Sair
          </button>
        </div>

        {error ? <p className="mt-6 rounded-xl bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

        {!user || !company ? (
          <p className="mt-8 text-slate-300">Carregando sua conta...</p>
        ) : (
          <div className="mt-8 space-y-4">
            <article className="rounded-2xl border border-white/10 bg-slate-900 p-5">
              <p className="text-sm text-slate-400">Usuário</p>
              <h2 className="mt-1 text-xl font-semibold">{user.name}</h2>
              <p className="mt-1 text-sm text-slate-300">{user.email}</p>
            </article>
            <article className="rounded-2xl border border-white/10 bg-slate-900 p-5">
              <p className="text-sm text-slate-400">Empresa</p>
              <h2 className="mt-1 text-xl font-semibold">{company.name}</h2>
              <p className="mt-1 text-sm text-slate-300">
                {company.segment}
                {company.city ? ` · ${company.city}` : ""}
                {company.state ? `/${company.state}` : ""}
              </p>
            </article>
            <p className="rounded-2xl bg-emerald-400/10 p-5 text-emerald-100">
              Base da conta criada. Próximo passo: cadastrar lançamentos financeiros.
            </p>
          </div>
        )}

        <Link className="mt-8 inline-block text-sm font-semibold text-emerald-300" href="/">
          Voltar para início
        </Link>
      </section>
    </main>
  );
}
