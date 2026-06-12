"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthCard } from "../../components/AuthCard";
import { AuthFormInput } from "../../components/AuthFormInput";
import { login, saveToken } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await login({ email, password });
      saveToken(response.access_token);
      router.push("/app");
    } catch {
      setError("E-mail ou senha inválidos.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthCard
      description="Entre para continuar de onde parou e ver a base da sua conta."
      eyebrow="Entrar"
      footerHref="/register"
      footerLinkLabel="Criar conta"
      footerText="Ainda não tem conta?"
      title="Acesse sua conta"
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <AuthFormInput
          autoComplete="email"
          label="E-mail"
          name="email"
          onChange={(event) => setEmail(event.target.value)}
          placeholder="joao@email.com"
          required
          type="email"
          value={email}
        />
        <AuthFormInput
          autoComplete="current-password"
          label="Senha"
          name="password"
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Sua senha"
          required
          type="password"
          value={password}
        />

        {error ? (
          <p className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
        ) : null}

        <button
          className="w-full rounded-2xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isSubmitting}
          type="submit"
        >
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </AuthCard>
  );
}
