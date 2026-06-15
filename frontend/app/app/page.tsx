"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  BreakEvenSummary,
  BusinessCostSummary,
  Company,
  FinancialSummary,
  User,
  getBreakEvenSummary,
  getBusinessCostSummary,
  getCurrentCompany,
  getCurrentUser,
  getFinancialSummary,
  isUnauthorizedError,
  readToken,
  removeToken,
} from "../../lib/api";

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const summaryStatusContent = {
  positive: {
    text: "Seu período está positivo.",
    className: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  },
  neutral: {
    text: "Seu período está zerado.",
    className: "border-sky-300/20 bg-sky-300/10 text-sky-100",
  },
  negative: {
    text: "Seu período está negativo.",
    className: "border-orange-300/20 bg-orange-300/10 text-orange-100",
  },
} satisfies Record<FinancialSummary["status"], { text: string; className: string }>;

const breakEvenStatusContent = {
  not_configured: {
    text: "Cadastre seus custos fixos para calcular este resumo.",
    className: "border-sky-300/20 bg-sky-300/10 text-sky-100",
  },
  below_break_even: {
    text: "Você ainda não cobriu seus custos fixos.",
    className: "border-orange-300/20 bg-orange-300/10 text-orange-100",
  },
  break_even_reached: {
    text: "Você já cobriu seus custos fixos.",
    className: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  },
} satisfies Record<BreakEvenSummary["status"], { text: string; className: string }>;

const fallbackBreakEvenNote =
  "Este é um cálculo simplificado. Ele considera apenas custos fixos ativos e receitas registradas. Ainda não considera margem por produto, custos variáveis ou CMV.";

const businessCostStatusText = {
  configured: "Seus custos fixos ativos já foram cadastrados.",
  empty: "Você ainda não cadastrou custos fixos ativos.",
} satisfies Record<BusinessCostSummary["status"], string>;

function formatCurrency(value: number) {
  return currencyFormatter.format(value);
}

function formatPercent(value: number | null) {
  if (value === null) {
    return "Cobertura ainda não calculada.";
  }

  return `${new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(value)}% dos custos fixos cobertos.`;
}

export default function AppPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [businessCostSummary, setBusinessCostSummary] = useState<BusinessCostSummary | null>(null);
  const [breakEvenSummary, setBreakEvenSummary] = useState<BreakEvenSummary | null>(null);
  const [error, setError] = useState("");
  const [businessCostError, setBusinessCostError] = useState("");
  const [breakEvenError, setBreakEvenError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = readToken();

    if (!token) {
      router.replace("/login");
      return;
    }

    const authToken = token;

    async function loadInitialData() {
      try {
        const [
          currentUser,
          currentCompany,
          currentSummary,
          currentBusinessCostSummary,
          currentBreakEvenSummary,
        ] = await Promise.allSettled([
          getCurrentUser(authToken),
          getCurrentCompany(authToken),
          getFinancialSummary(authToken),
          getBusinessCostSummary(authToken),
          getBreakEvenSummary(authToken),
        ]);

        const expiredSession = [
          currentUser,
          currentCompany,
          currentSummary,
          currentBusinessCostSummary,
          currentBreakEvenSummary,
        ].some((result) => result.status === "rejected" && isUnauthorizedError(result.reason));

        if (expiredSession) {
          removeToken();
          setError("Sua sessão expirou. Entre novamente.");
          router.replace("/login");
          return;
        }

        if (currentUser.status === "fulfilled") {
          setUser(currentUser.value);
        }

        if (currentCompany.status === "fulfilled") {
          setCompany(currentCompany.value);
        }

        if (currentSummary.status === "fulfilled") {
          setSummary(currentSummary.value);
        } else {
          setError("Não foi possível carregar seu resumo financeiro.");
        }

        if (currentBusinessCostSummary.status === "fulfilled") {
          setBusinessCostSummary(currentBusinessCostSummary.value);
        } else {
          setBusinessCostError("Não foi possível carregar seus custos fixos.");
        }

        if (currentBreakEvenSummary.status === "fulfilled") {
          setBreakEvenSummary(currentBreakEvenSummary.value);
        } else {
          setBreakEvenError("Não foi possível carregar o ponto de equilíbrio.");
        }
      } finally {
        setIsLoading(false);
      }
    }

    loadInitialData();
  }, [router]);

  function handleLogout() {
    removeToken();
    router.push("/login");
  }

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
        <p className="text-sm text-slate-300">Carregando seu resumo financeiro...</p>
      </main>
    );
  }

  const statusContent = summary ? summaryStatusContent[summary.status] : null;

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

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">
                Resumo financeiro
              </p>
              <h2 className="mt-2 text-2xl font-bold text-white">Visão simples do período</h2>
            </div>
            <div className="flex flex-col gap-3 sm:items-end">
              <Link
                className="inline-flex rounded-2xl bg-emerald-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
                href="/app/entries"
              >
                Cadastrar receitas e despesas
              </Link>
              <Link
                className="inline-flex rounded-2xl border border-emerald-300/30 px-5 py-3 text-sm font-semibold text-emerald-100 transition hover:border-emerald-200 hover:bg-emerald-400/10"
                href="/app/business-costs"
              >
                Cadastrar custos fixos
              </Link>
            </div>
          </div>

          {summary ? (
            <div className="mt-6">
              {summary.entries_count === 0 ? (
                <p className="rounded-2xl border border-sky-300/20 bg-sky-300/10 p-4 text-sm leading-6 text-sky-100">
                  Você ainda não tem lançamentos. Cadastre suas primeiras receitas e despesas para
                  ver seu resumo.
                </p>
              ) : null}

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Entradas</p>
                  <p className="mt-2 text-2xl font-bold text-emerald-200">
                    {formatCurrency(summary.total_revenue)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Saídas</p>
                  <p className="mt-2 text-2xl font-bold text-orange-200">
                    {formatCurrency(summary.total_expense)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Saldo</p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {formatCurrency(summary.net_result)}
                  </p>
                </div>
                {statusContent ? (
                  <div className={`rounded-2xl border p-4 ${statusContent.className}`}>
                    <p className="text-sm opacity-80">Situação</p>
                    <p className="mt-2 text-lg font-semibold">{statusContent.text}</p>
                  </div>
                ) : null}
              </div>

              <p className="mt-4 text-sm text-slate-300">
                Lançamentos considerados: {summary.entries_count}
              </p>
            </div>
          ) : null}
        </section>


        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">
              Ponto de equilíbrio simplificado
            </p>
            <h2 className="mt-2 text-2xl font-bold text-white">Receitas cobrindo custos fixos</h2>
          </div>

          {breakEvenError ? (
            <p className="mt-6 rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {breakEvenError}
            </p>
          ) : null}

          {breakEvenSummary ? (
            <div className="mt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Custos fixos mensais</p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {formatCurrency(breakEvenSummary.monthly_fixed_costs)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Receita necessária</p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {formatCurrency(breakEvenSummary.break_even_revenue)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Receita registrada</p>
                  <p className="mt-2 text-2xl font-bold text-emerald-200">
                    {formatCurrency(breakEvenSummary.period_revenue)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Falta para cobrir</p>
                  <p className="mt-2 text-2xl font-bold text-orange-100">
                    {formatCurrency(breakEvenSummary.revenue_gap)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Cobertura</p>
                  <p className="mt-2 text-lg font-semibold text-slate-100">
                    {formatPercent(breakEvenSummary.coverage_percent)}
                  </p>
                </div>
                <div
                  className={`rounded-2xl border p-4 ${
                    breakEvenStatusContent[breakEvenSummary.status].className
                  }`}
                >
                  <p className="text-sm opacity-80">Situação</p>
                  <p className="mt-2 text-lg font-semibold">
                    {breakEvenStatusContent[breakEvenSummary.status].text}
                  </p>
                </div>
              </div>

              <p className="mt-4 rounded-2xl border border-white/10 bg-slate-950/40 p-4 text-sm leading-6 text-slate-300">
                {breakEvenSummary.note || fallbackBreakEvenNote}
              </p>
            </div>
          ) : null}
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">
                Custos fixos mensais
              </p>
              <h2 className="mt-2 text-2xl font-bold text-white">Base para entender seu negócio</h2>
            </div>
            <Link
              className="inline-flex rounded-2xl border border-emerald-300/30 px-5 py-3 text-sm font-semibold text-emerald-100 transition hover:border-emerald-200 hover:bg-emerald-400/10"
              href="/app/business-costs"
            >
              Cadastrar custos fixos
            </Link>
          </div>

          {businessCostError ? (
            <p className="mt-6 rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {businessCostError}
            </p>
          ) : null}

          {businessCostSummary ? (
            <div className="mt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-950/60 p-4 sm:col-span-2">
                  <p className="text-sm text-slate-400">Total mensal ativo</p>
                  <p className="mt-2 text-3xl font-bold text-emerald-200">
                    {formatCurrency(businessCostSummary.total_active_monthly_costs)}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Custos ativos</p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {businessCostSummary.active_costs_count}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Custos inativos</p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {businessCostSummary.inactive_costs_count}
                  </p>
                </div>
                <div className="rounded-2xl bg-slate-950/60 p-4">
                  <p className="text-sm text-slate-400">Total cadastrado</p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {businessCostSummary.total_costs_count}
                  </p>
                </div>
                <div className="rounded-2xl border border-sky-300/20 bg-sky-300/10 p-4 text-sky-100">
                  <p className="text-sm opacity-80">Situação</p>
                  <p className="mt-2 text-lg font-semibold">
                    {businessCostStatusText[businessCostSummary.status]}
                  </p>
                </div>
              </div>

              {businessCostSummary.status === "empty" ? (
                <p className="mt-4 rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-4 text-sm leading-6 text-emerald-100">
                  Cadastre contas como aluguel, energia, internet e contador para entender melhor seu
                  negócio.
                </p>
              ) : null}
            </div>
          ) : null}
        </section>
      </section>
    </main>
  );
}
