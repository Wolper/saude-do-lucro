"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import {
  BusinessCost,
  BusinessCostStatusFilter,
  createBusinessCost,
  deleteBusinessCost,
  isUnauthorizedError,
  listBusinessCosts,
  readToken,
  removeToken,
  updateBusinessCost,
} from "../../../lib/api";

type FormState = {
  name: string;
  category: string;
  amount: string;
  is_active: boolean;
  notes: string;
};

const initialFormState: FormState = {
  name: "",
  category: "aluguel",
  amount: "",
  is_active: true,
  notes: "",
};

const filterOptions: Array<{ label: string; value: BusinessCostStatusFilter }> = [
  { label: "Todos", value: "all" },
  { label: "Ativos", value: "active" },
  { label: "Inativos", value: "inactive" },
];

const categoryOptions = ["aluguel", "energia", "folha", "serviços", "impostos", "outros"];

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

export default function BusinessCostsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [costs, setCosts] = useState<BusinessCost[]>([]);
  const [filter, setFilter] = useState<BusinessCostStatusFilter>("all");
  const [form, setForm] = useState<FormState>(initialFormState);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [changingId, setChangingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [validationMessage, setValidationMessage] = useState("");

  const emptyStateText = useMemo(
    () =>
      "Você ainda não cadastrou custos fixos. Cadastre contas como aluguel, energia e internet para entender melhor seu negócio.",
    [],
  );

  const handleExpiredSession = useCallback(() => {
    removeToken();
    setError("Sua sessão expirou. Entre novamente.");
    router.replace("/login");
  }, [router]);

  const loadCosts = useCallback(
    async (authToken: string, selectedFilter: BusinessCostStatusFilter) => {
      setIsLoading(true);
      setError("");

      try {
        const businessCosts = await listBusinessCosts(authToken, selectedFilter);
        setCosts(businessCosts);
      } catch (loadError) {
        if (isUnauthorizedError(loadError)) {
          handleExpiredSession();
          return;
        }

        setError("Não foi possível carregar seus custos fixos.");
      } finally {
        setIsLoading(false);
      }
    },
    [handleExpiredSession],
  );

  useEffect(() => {
    const storedToken = readToken();

    if (!storedToken) {
      router.replace("/login");
      return;
    }

    setToken(storedToken);
    loadCosts(storedToken, filter);
  }, [filter, loadCosts, router]);

  function updateForm(field: keyof FormState, value: string | boolean) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccessMessage("");
    setValidationMessage("");

    const amount = Number(form.amount);

    if (!Number.isFinite(amount) || amount <= 0) {
      setValidationMessage("Informe um valor mensal maior que zero.");
      return;
    }

    if (!token) {
      router.replace("/login");
      return;
    }

    setIsSaving(true);

    try {
      await createBusinessCost(token, {
        name: form.name.trim(),
        category: form.category.trim(),
        amount,
        is_active: form.is_active,
        notes: form.notes.trim() || null,
      });
      setForm(initialFormState);
      setSuccessMessage("Custo fixo salvo com sucesso.");
      await loadCosts(token, filter);
    } catch (saveError) {
      if (isUnauthorizedError(saveError)) {
        handleExpiredSession();
        return;
      }

      setError("Não foi possível salvar o custo fixo.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleToggle(cost: BusinessCost) {
    if (!token) {
      router.replace("/login");
      return;
    }

    setError("");
    setSuccessMessage("");
    setChangingId(cost.id);

    try {
      await updateBusinessCost(token, cost.id, {
        name: cost.name,
        category: cost.category,
        amount: cost.amount,
        is_active: !cost.is_active,
        notes: cost.notes,
      });
      setSuccessMessage(`Custo fixo ${cost.is_active ? "desativado" : "ativado"} com sucesso.`);
      await loadCosts(token, filter);
    } catch (updateError) {
      if (isUnauthorizedError(updateError)) {
        handleExpiredSession();
        return;
      }

      setError("Não foi possível atualizar o custo fixo.");
    } finally {
      setChangingId(null);
    }
  }

  async function handleDelete(cost: BusinessCost) {
    const confirmed = window.confirm("Excluir este custo fixo?");

    if (!confirmed || !token) {
      return;
    }

    setError("");
    setSuccessMessage("");
    setDeletingId(cost.id);

    try {
      await deleteBusinessCost(token, cost.id);
      setCosts((currentCosts) => currentCosts.filter((item) => item.id !== cost.id));
      setSuccessMessage("Custo fixo excluído com sucesso.");
    } catch (deleteError) {
      if (isUnauthorizedError(deleteError)) {
        handleExpiredSession();
        return;
      }

      setError("Não foi possível excluir o custo fixo.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-6 text-white sm:px-6 sm:py-8">
      <section className="mx-auto flex w-full max-w-4xl flex-col gap-5">
        <header className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 shadow-2xl shadow-emerald-950/25 sm:p-6">
          <Link className="text-sm font-semibold text-emerald-200 transition hover:text-emerald-100" href="/app">
            ← Voltar para a área inicial
          </Link>
          <div className="mt-5 flex flex-col gap-2">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-emerald-300">
              Custos fixos
            </p>
            <h1 className="text-3xl font-bold tracking-tight">Contas mensais do negócio</h1>
            <p className="max-w-2xl text-sm leading-6 text-slate-300">
              Cadastre contas recorrentes como aluguel, energia, internet, contador e salários.
            </p>
          </div>
        </header>

        {error ? <p className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p> : null}

        {successMessage ? (
          <p className="rounded-2xl bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
            {successMessage}
          </p>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 sm:p-6" id="novo-custo-fixo">
          <h2 className="text-xl font-bold text-white">Novo custo fixo</h2>
          <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-semibold text-slate-200">
                Nome
                <input
                  className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300"
                  maxLength={120}
                  onChange={(event) => updateForm("name", event.target.value)}
                  placeholder="Aluguel"
                  required
                  type="text"
                  value={form.name}
                />
              </label>

              <label className="grid gap-2 text-sm font-semibold text-slate-200">
                Categoria
                <select
                  className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-emerald-300"
                  onChange={(event) => updateForm("category", event.target.value)}
                  value={form.category}
                >
                  {categoryOptions.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="grid gap-2 text-sm font-semibold text-slate-200">
              Valor mensal
              <input
                className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300"
                min="0.01"
                onChange={(event) => updateForm("amount", event.target.value)}
                placeholder="0,00"
                required
                step="0.01"
                type="number"
                value={form.amount}
              />
            </label>

            <label className="flex items-center gap-3 rounded-2xl bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200">
              <input
                checked={form.is_active}
                className="h-4 w-4 accent-emerald-400"
                onChange={(event) => updateForm("is_active", event.target.checked)}
                type="checkbox"
              />
              Este custo está ativo
            </label>

            <label className="grid gap-2 text-sm font-semibold text-slate-200">
              Observações
              <textarea
                className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300"
                maxLength={500}
                onChange={(event) => updateForm("notes", event.target.value)}
                placeholder="Ponto comercial"
                value={form.notes}
              />
            </label>

            {validationMessage ? (
              <p className="rounded-2xl bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
                {validationMessage}
              </p>
            ) : null}

            <button
              className="rounded-2xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isSaving}
              type="submit"
            >
              {isSaving ? "Salvando..." : "Salvar custo fixo"}
            </button>
          </form>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Custos fixos cadastrados</h2>
              <p className="mt-1 text-sm text-slate-300">Use o filtro para ver todos, ativos ou inativos.</p>
            </div>
            <div className="grid grid-cols-3 gap-2 rounded-2xl bg-slate-950/60 p-1">
              {filterOptions.map((option) => (
                <button
                  className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
                    filter === option.value
                      ? "bg-emerald-400 text-slate-950"
                      : "text-slate-300 hover:bg-white/10 hover:text-white"
                  }`}
                  key={option.value}
                  onClick={() => setFilter(option.value)}
                  type="button"
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5 grid gap-3">
            {isLoading ? <p className="text-sm text-slate-300">Carregando seus custos fixos...</p> : null}

            {!isLoading && costs.length === 0 ? (
              <div className="rounded-2xl bg-slate-950/60 px-4 py-5 text-sm leading-6 text-slate-300">
                <p>{emptyStateText}</p>
                <a className="mt-3 inline-flex text-sm font-semibold text-emerald-200" href="#novo-custo-fixo">
                  Cadastrar custo fixo
                </a>
              </div>
            ) : null}

            {!isLoading
              ? costs.map((cost) => (
                  <article
                    className="rounded-2xl border border-white/10 bg-slate-950/60 p-4"
                    key={cost.id}
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <span
                          className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${
                            cost.is_active
                              ? "bg-emerald-400/15 text-emerald-100"
                              : "bg-slate-400/15 text-slate-200"
                          }`}
                        >
                          {cost.is_active ? "Ativo" : "Inativo"}
                        </span>
                        <h3 className="mt-3 text-lg font-bold text-white">{cost.name}</h3>
                        <p className="mt-1 text-sm text-slate-300">Categoria: {cost.category}</p>
                        {cost.notes ? <p className="mt-2 text-sm leading-6 text-slate-300">{cost.notes}</p> : null}
                      </div>
                      <div className="flex flex-col gap-3 sm:items-end">
                        <p className="text-2xl font-bold text-emerald-100">
                          {currencyFormatter.format(cost.amount)}
                        </p>
                        <div className="flex flex-wrap gap-2 sm:justify-end">
                          <button
                            className="rounded-2xl border border-emerald-300/30 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:border-emerald-200 hover:bg-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                            disabled={changingId === cost.id}
                            onClick={() => handleToggle(cost)}
                            type="button"
                          >
                            {changingId === cost.id
                              ? "Atualizando..."
                              : cost.is_active
                                ? "Desativar"
                                : "Ativar"}
                          </button>
                          <button
                            className="rounded-2xl border border-rose-300/30 px-4 py-2 text-sm font-semibold text-rose-100 transition hover:border-rose-200 hover:bg-rose-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                            disabled={deletingId === cost.id}
                            onClick={() => handleDelete(cost)}
                            type="button"
                          >
                            {deletingId === cost.id ? "Excluindo..." : "Excluir"}
                          </button>
                        </div>
                      </div>
                    </div>
                  </article>
                ))
              : null}
          </div>
        </section>
      </section>
    </main>
  );
}
