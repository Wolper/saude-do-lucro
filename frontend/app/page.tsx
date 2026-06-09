type HealthPayload = {
  status: string;
  service: string;
  version: string;
};

const conceptCards = [
  {
    title: "Saúde financeira",
    description: "Entenda de forma simples se o negócio está saudável ou precisa de atenção.",
  },
  {
    title: "Ponto de equilíbrio",
    description: "Veja quanto precisa vender para cobrir custos e parar de trabalhar no escuro.",
  },
  {
    title: "Margem por produto",
    description: "Identifique quais produtos sustentam o resultado e quais podem estar drenando lucro.",
  },
  {
    title: "Recomendações práticas",
    description: "Receba orientações diretas para melhorar lucratividade sem virar um ERP.",
  },
];

async function getApiHealth(): Promise<HealthPayload | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    return null;
  }

  try {
    const response = await fetch(`${apiUrl}/health`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as HealthPayload;
  } catch {
    return null;
  }
}

export default async function Home() {
  const apiHealth = await getApiHealth();

  return (
    <main className="min-h-screen px-5 py-8 text-lucro-950 sm:px-8 lg:px-16">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-10 rounded-[2rem] border border-green-100 bg-white/80 p-6 shadow-2xl shadow-green-900/10 backdrop-blur sm:p-10 lg:grid lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div className="space-y-7">
          <span className="inline-flex rounded-full bg-green-100 px-4 py-2 text-sm font-semibold text-lucro-700">
            Fundação técnica inicial
          </span>
          <div className="space-y-4">
            <h1 className="text-4xl font-black tracking-tight text-lucro-950 sm:text-5xl lg:text-6xl">
              Saúde do Lucro
            </h1>
            <p className="max-w-2xl text-xl font-semibold text-green-900 sm:text-2xl">
              Seu copiloto de lucratividade para negócios de alimentação.
            </p>
            <p className="max-w-2xl text-base leading-7 text-slate-700 sm:text-lg">
              Uma aplicação simples para ajudar restaurantes, trailers, hamburguerias, pizzarias,
              lanchonetes, açaiterias, food trucks e negócios familiares a tomar decisões melhores
              sobre lucro, custos e preços.
            </p>
          </div>
          <div className="rounded-2xl border border-green-200 bg-green-50 p-4 text-sm text-green-900">
            <strong>Status da API:</strong>{" "}
            {apiHealth?.status === "ok"
              ? `${apiHealth.service} ${apiHealth.version} online`
              : "indisponível no momento — a tela continua funcionando."}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {conceptCards.map((card) => (
            <article key={card.title} className="rounded-3xl border border-green-100 bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold text-lucro-950">{card.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">{card.description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
