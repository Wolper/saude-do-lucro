"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    const data = await response.json();
    setLoading(false);

    if (!response.ok) {
      setError(data.detail ?? "Não foi possível entrar.");
      return;
    }

    localStorage.setItem("saude_do_lucro_token", data.access_token);
    router.push("/app");
  }

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-white">
      <section className="mx-auto max-w-md rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-emerald-950/20">
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">
          Entrar
        </p>
        <h1 className="mt-3 text-3xl font-bold">Acesse sua conta</h1>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Entre para ver a empresa vinculada à sua conta.
        </p>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-200">
            E-mail
            <input className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none focus:border-emerald-300" name="email" required type="email" />
          </label>
          <label className="block text-sm font-medium text-slate-200">
            Senha
            <input className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none focus:border-emerald-300" name="password" required type="password" />
          </label>

          {error ? <p className="rounded-xl bg-red-500/10 p-3 text-sm text-red-200">{error}</p> : null}

          <button className="w-full rounded-xl bg-emerald-400 px-4 py-3 font-semibold text-slate-950 disabled:opacity-60" disabled={loading} type="submit">
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-300">
          Ainda não tem conta? <Link className="font-semibold text-emerald-300" href="/register">Criar conta</Link>
        </p>
      </section>
    </main>
  );
}
