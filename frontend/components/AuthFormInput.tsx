import type { ComponentPropsWithoutRef } from "react";

type AuthFormInputProps = ComponentPropsWithoutRef<"input"> & {
  label: string;
};

export function AuthFormInput({ label, id, ...props }: AuthFormInputProps) {
  const inputId = id ?? props.name;

  return (
    <label className="block text-sm font-medium text-slate-100" htmlFor={inputId}>
      {label}
      <input
        className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-base text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300 focus:ring-2 focus:ring-emerald-300/20"
        id={inputId}
        {...props}
      />
    </label>
  );
}
