import Link from "next/link";

const pillars = [
  "Saúde financeira",
  "Ponto de equilíbrio",
  "Margem por produto",
  "Recomendações práticas",
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen w-full max-w-5xl flex-col justify-center px-6 py-16">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-emerald-300">
          Saúde do Lucro
        </p>
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
          Seu copiloto de lucratividade para negócios de alimentação
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Uma fundação simples para ajudar restaurantes, trailers, hamburguerias
          e outros negócios de alimentação a entenderem se estão lucrando.
        </p>

        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Link
            className="rounded-2xl bg-emerald-400 px-6 py-3 text-center font-semibold text-slate-950 transition hover:bg-emerald-300"
            href="/register"
          >
            Criar conta
          </Link>
          <Link
            className="rounded-2xl border border-white/10 px-6 py-3 text-center font-semibold text-slate-100 transition hover:border-emerald-300 hover:text-emerald-200"
            href="/login"
          >
            Entrar
          </Link>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {pillars.map((pillar) => (
            <article
              className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-2xl shadow-emerald-950/20"
              key={pillar}
            >
              <h2 className="text-base font-semibold text-emerald-100">{pillar}</h2>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
