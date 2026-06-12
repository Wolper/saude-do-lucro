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

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new Error("Request failed");
  }

  return response.json() as Promise<T>;
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

export function saveToken(token: string) {
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function readToken() {
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function removeToken() {
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}
