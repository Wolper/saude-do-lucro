"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { AuthCard } from "../../components/AuthCard";
import { AuthFormInput } from "../../components/AuthFormInput";
import { register, saveToken } from "../../lib/api";

const initialForm = {
  name: "",
  email: "",
  password: "",
  company_name: "",
  segment: "",
  city: "",
  state: "",
};

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await register({
        ...form,
        state: form.state.trim().toUpperCase(),
      });
      saveToken(response.access_token);
      router.push("/app");
    } catch {
      setError("Não foi possível criar sua conta.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function updateField(field: keyof typeof form, value: string) {
    setForm((currentForm) => ({ ...currentForm, [field]: value }));
  }

  return (
    <AuthCard
      description="Crie uma conta simples para começar a organizar a saúde do seu negócio de alimentação."
      eyebrow="Criar conta"
      footerHref="/login"
      footerLinkLabel="Entrar"
      footerText="Já tem conta?"
      title="Comece com seus dados básicos"
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <AuthFormInput
          autoComplete="name"
          label="Seu nome"
          name="name"
          onChange={(event) => updateField("name", event.target.value)}
          placeholder="João"
          required
          type="text"
          value={form.name}
        />
        <AuthFormInput
          autoComplete="email"
          label="E-mail"
          name="email"
          onChange={(event) => updateField("email", event.target.value)}
          placeholder="joao@email.com"
          required
          type="email"
          value={form.email}
        />
        <AuthFormInput
          autoComplete="new-password"
          label="Senha"
          minLength={8}
          name="password"
          onChange={(event) => updateField("password", event.target.value)}
          placeholder="Pelo menos 8 caracteres"
          required
          type="password"
          value={form.password}
        />
        <AuthFormInput
          autoComplete="organization"
          label="Nome da empresa"
          name="company_name"
          onChange={(event) => updateField("company_name", event.target.value)}
          placeholder="MM Chicken"
          required
          type="text"
          value={form.company_name}
        />
        <AuthFormInput
          label="Segmento"
          name="segment"
          onChange={(event) => updateField("segment", event.target.value)}
          placeholder="Hamburgueria, pizzaria, marmitaria..."
          required
          type="text"
          value={form.segment}
        />
        <div className="grid gap-4 sm:grid-cols-[1fr_96px]">
          <AuthFormInput
            autoComplete="address-level2"
            label="Cidade"
            name="city"
            onChange={(event) => updateField("city", event.target.value)}
            placeholder="São Paulo"
            required
            type="text"
            value={form.city}
          />
          <AuthFormInput
            autoComplete="address-level1"
            label="Estado"
            maxLength={2}
            name="state"
            onChange={(event) => updateField("state", event.target.value)}
            placeholder="SP"
            required
            type="text"
            value={form.state}
          />
        </div>

        {error ? (
          <p className="rounded-2xl bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
        ) : null}

        <button
          className="w-full rounded-2xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isSubmitting}
          type="submit"
        >
          {isSubmitting ? "Criando conta..." : "Criar conta"}
        </button>
      </form>
    </AuthCard>
  );
}
