"use client";

// Source sanitized to avoid hidden or bidirectional Unicode control characters.
import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import {
  FinancialEntry,
  FinancialEntryType,
  createFinancialEntry,
  deleteFinancialEntry,
  isUnauthorizedError,
  listFinancialEntries,
  readToken,
  removeToken,
} from "../../../lib/api";

type EntryFilter = "all" | FinancialEntryType;

type FormState = {
  type: FinancialEntryType;
  category: string;
  description: string;
  amount: string;
  payment_method: string;
  entry_date: string;
};

const initialFormState: FormState = {
  type: "revenue",
  category: "",
  description: "",
  amount: "",
  payment_method: "pix",
  entry_date: new Date().toISOString().slice(0, 10),
};

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  timeZone: "UTC",
});

const filterOptions: Array<{ label: string; value: EntryFilter }> = [
  { label: "Todos", value: "all" },
  { label: "Receitas", value: "revenue" },
  { label: "Despesas", value: "expense" },
];

function getTypeLabel(type: FinancialEntryType) {
  return type === "revenue" ? "Receita" : "Despesa";
}

function formatDate(date: string) {
  return dateFormatter.format(new Date(`${date}T00:00:00Z`));
}

export default function EntriesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [entries, setEntries] = useState<FinancialEntry[]>([]);
  const [filter, setFilter] = useState<EntryFilter>("all");
  const [form, setForm] = useState<FormState>(initialFormState);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [validationMessage, setValidationMessage] = useState("");

  const selectedType = useMemo(() => (filter === "all" ? undefined : filter), [filter]);

  const handleExpiredSession = useCallback(() => {
    removeToken();
    setError("Sua sessão expirou. Entre novamente.");
    router.replace("/login");
  }, [router]);

  const loadEntries = useCallback(
    async (authToken: string, entryType?: FinancialEntryType) => {
      setIsLoading(true);
      setError("");

      try {
        const financialEntries = await listFinancialEntries(authToken, entryType);
        setEntries(financialEntries);
      } catch (loadError) {
        if (isUnauthorizedError(loadError)) {
          handleExpiredSession();
          return;
        }

        setError("Não foi possível carregar seus lançamentos.");
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
    loadEntries(storedToken, selectedType);
  }, [loadEntries, router, selectedType]);

  function updateForm(field: keyof FormState, value: string) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccessMessage("");
    setValidationMessage("");

    const amount = Number(form.amount);

    if (!Number.isFinite(amount) || amount <= 0) {
      setValidationMessage("Informe um valor maior que zero.");
      return;
    }

    if (!token) {
      router.replace("/login");
      return;
    }

    setIsSaving(true);

    try {
      await createFinancialEntry(token, {
        type: form.type,
        category: form.category.trim(),
        description: form.description.trim() || null,
        amount,
        payment_method: form.payment_method,
        entry_date: form.entry_date,
        source: "manual",
      });
      setForm({ ...initialFormState, type: form.type });
      setSuccessMessage("Lançamento salvo com sucesso.");
      await loadEntries(token, selectedType);
    } catch (saveError) {
      if (isUnauthorizedError(saveError)) {
        handleExpiredSession();
        return;
      }

      setError("Não foi possível salvar o lançamento.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(entry: FinancialEntry) {
    const confirmed = window.confirm("Excluir este lançamento?");

    if (!confirmed || !token) {
      return;
    }

    setError("");
    setSuccessMessage("");
    setDeletingId(entry.id);

    try {
      await deleteFinancialEntry(token, entry.id);
      setEntries((currentEntries) => currentEntries.filter((item) => item.id !== entry.id));
      setSuccessMessage("Lançamento excluído com sucesso.");
    } catch (deleteError) {
      if (isUnauthorizedError(deleteError)) {
        handleExpiredSession();
        return;
      }

      setError("Não foi possível excluir o lançamento.");
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
              Lançamentos financeiros
            </p>
            <h1 className="text-3xl font-bold tracking-tight">Receitas e despesas</h1>
            <p className="max-w-2xl text-sm leading-6 text-slate-300">
              Cadastre rapidamente o que entrou e saiu do caixa. Sem dashboard, gráficos ou regras
              complexas por enquanto.
            </p>
          </div>
        </header>

        {error ? (
          <p className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
        ) : null}

        {successMessage ? (
          <p className="rounded-2xl bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
            {successMessage}
          </p>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 sm:p-6">
          <h2 className="text-xl font-bold text-white">Novo lançamento</h2>
          <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
            <label className="grid gap-2 text-sm font-semibold text-slate-200">
              Tipo
              <select
                className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-emerald-300"
                onChange={(event) => updateForm("type", event.target.value)}
                value={form.type}
              >
                <option value="revenue">Receita</option>
                <option value="expense">Despesa</option>
              </select>
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-semibold text-slate-200">
                Categoria
                <input
                  className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300"
                  maxLength={120}
                  onChange={(event) => updateForm("category", event.target.value)}
                  placeholder="Ex.: balcão, aluguel"
                  required
                  type="text"
                  value={form.category}
                />
              </label>

              <label className="grid gap-2 text-sm font-semibold text-slate-200">
                Valor
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
            </div>

            <label className="grid gap-2 text-sm font-semibold text-slate-200">
              Descrição
              <input
                className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300"
                maxLength={255}
                onChange={(event) => updateForm("description", event.target.value)}
                placeholder="Ex.: Vendas do dia"
                type="text"
                value={form.description}
              />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-semibold text-slate-200">
                Forma de pagamento
                <select
                  className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-emerald-300"
                  onChange={(event) => updateForm("payment_method", event.target.value)}
                  value={form.payment_method}
                >
                  <option value="pix">pix</option>
                  <option value="cartão">cartão</option>
                  <option value="dinheiro">dinheiro</option>
                  <option value="outro">outro</option>
                </select>
              </label>

              <label className="grid gap-2 text-sm font-semibold text-slate-200">
                Data
                <input
                  className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-white outline-none transition focus:border-emerald-300"
                  onChange={(event) => updateForm("entry_date", event.target.value)}
                  required
                  type="date"
                  value={form.entry_date}
                />
              </label>
            </div>

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
              {isSaving ? "Salvando..." : "Salvar lançamento"}
            </button>
          </form>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Lançamentos cadastrados</h2>
              <p className="mt-1 text-sm text-slate-300">Use o filtro para ver só receitas ou despesas.</p>
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
            {isLoading ? <p className="text-sm text-slate-300">Carregando seus lançamentos...</p> : null}

            {!isLoading && entries.length === 0 ? (
              <p className="rounded-2xl bg-slate-950/60 px-4 py-5 text-sm text-slate-300">
                Nenhum lançamento encontrado.
              </p>
            ) : null}

            {!isLoading
              ? entries.map((entry) => (
                  <article
                    className="rounded-2xl border border-white/10 bg-slate-950/60 p-4"
                    key={entry.id}
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <span
                          className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${
                            entry.type === "revenue"
                              ? "bg-emerald-400/15 text-emerald-100"
                              : "bg-rose-400/15 text-rose-100"
                          }`}
                        >
                          {getTypeLabel(entry.type)}
                        </span>
                        <h3 className="mt-3 text-lg font-bold text-white">{entry.category}</h3>
                        {entry.description ? (
                          <p className="mt-1 text-sm leading-6 text-slate-300">{entry.description}</p>
                        ) : null}
                        <dl className="mt-3 grid gap-2 text-sm text-slate-300 sm:grid-cols-2">
                          <div>
                            <dt className="text-slate-500">Data</dt>
                            <dd>{formatDate(entry.entry_date)}</dd>
                          </div>
                          <div>
                            <dt className="text-slate-500">Forma de pagamento</dt>
                            <dd>{entry.payment_method || "Não informada"}</dd>
                          </div>
                        </dl>
                      </div>
                      <div className="flex flex-col gap-3 sm:items-end">
                        <p className="text-2xl font-bold text-emerald-100">
                          {currencyFormatter.format(entry.amount)}
                        </p>
                        <button
                          className="rounded-2xl border border-rose-300/30 px-4 py-2 text-sm font-semibold text-rose-100 transition hover:border-rose-200 hover:bg-rose-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={deletingId === entry.id}
                          onClick={() => handleDelete(entry)}
                          type="button"
                        >
                          {deletingId === entry.id ? "Excluindo..." : "Excluir"}
                        </button>
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
