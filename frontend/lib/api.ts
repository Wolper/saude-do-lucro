const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const AUTH_TOKEN_KEY = "saude_do_lucro_token";

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = LoginPayload & {
  name: string;
  company_name: string;
  segment: string;
  city: string;
  state: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type User = {
  id: number;
  name: string;
  email: string;
};

export type Company = {
  id: number;
  name: string;
  segment: string;
};

export type FinancialEntryType = "revenue" | "expense";

export type FinancialEntry = {
  id: number;
  company_id: number;
  type: FinancialEntryType;
  category: string;
  description: string | null;
  amount: number;
  payment_method: string | null;
  entry_date: string;
  source: string;
  created_at: string;
  updated_at: string;
};

export type FinancialEntryPayload = {
  type: FinancialEntryType;
  category: string;
  description?: string | null;
  amount: number;
  payment_method?: string | null;
  entry_date: string;
  source: string;
};

export type FinancialSummaryStatus = "positive" | "neutral" | "negative";

export type FinancialSummary = {
  total_revenue: number;
  total_expense: number;
  net_result: number;
  status: FinancialSummaryStatus;
  entries_count: number;
  start_date: string | null;
  end_date: string | null;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number) {
    super("Request failed");
    this.status = status;
  }
}

export function isUnauthorizedError(error: unknown) {
  return error instanceof ApiError && error.status === 401;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<T>;
}

async function requestWithoutBody(path: string, init: RequestInit = {}): Promise<void> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }
}

export function register(payload: RegisterPayload) {
  return request<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(payload: LoginPayload) {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser(token: string) {
  return request<User>("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function getCurrentCompany(token: string) {
  return request<Company>("/companies/current", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function getFinancialSummary(token: string) {
  return request<FinancialSummary>("/financial-summary", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function listFinancialEntries(token: string, type?: FinancialEntryType) {
  const params = type ? `?type=${type}` : "";

  return request<FinancialEntry[]>(`/financial-entries${params}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function createFinancialEntry(token: string, payload: FinancialEntryPayload) {
  return request<FinancialEntry>("/financial-entries", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
}

export function deleteFinancialEntry(token: string, entryId: number) {
  return requestWithoutBody(`/financial-entries/${entryId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export function saveToken(token: string) {
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function readToken() {
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function removeToken() {
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}
