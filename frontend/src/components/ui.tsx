import type { ReactNode } from "react";
import { Check } from "lucide-react";
import type { Decision } from "../lib/api";

export const STEPS = ["Akademisyen", "İşlem", "Yıl", "WoS / Scopus", "Sonuçlar"];

export function Stepper({ current }: { current: number }) {
  return (
    <ol className="flex items-center gap-2 sm:gap-4">
      {STEPS.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <li key={label} className="flex items-center gap-2">
            <span
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
                done ? "bg-maku-500 text-white" : active ? "bg-maku-100 text-maku-700 ring-2 ring-maku-500" : "bg-slate-200 text-slate-500"
              }`}
            >
              {done ? <Check size={16} /> : i + 1}
            </span>
            <span className={`hidden text-sm sm:inline ${active ? "font-semibold text-slate-900" : "text-slate-500"}`}>{label}</span>
            {i < STEPS.length - 1 && <span className="h-px w-6 bg-slate-300 sm:w-10" />}
          </li>
        );
      })}
    </ol>
  );
}

export function Card({ children, className = "", padded = true }: { children: ReactNode; className?: string; padded?: boolean }) {
  return <div className={`rounded-2xl border border-slate-200 bg-white shadow-sm ${padded ? "p-6" : ""} ${className}`}>{children}</div>;
}

const DECISION_STYLE: Record<Decision, [string, string]> = {
  accepted: ["Kabul", "bg-emerald-100 text-emerald-800"],
  rejected: ["Kabul edilmez", "bg-rose-100 text-rose-800"],
  manual_check: ["Kontrol gerekli", "bg-amber-100 text-amber-800"],
};

export function DecisionBadge({ decision }: { decision: Decision }) {
  const [text, cls] = DECISION_STYLE[decision];
  return <span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ${cls}`}>{text}</span>;
}

const INDEX_NAMES: Record<string, string> = {
  SCIE: "SCI-Expanded",
  SSCI: "SSCI",
  AHCI: "AHCI",
  ESCI: "ESCI",
  SCOPUS: "Scopus",
  TR_DIZIN: "TR Dizin",
  OTHER_INTERNATIONAL: "Diğer uluslararası",
  INTERNATIONAL_BOOK: "Uluslararası kitap",
};

export function IndexBadge({ index }: { index: string }) {
  if (!INDEX_NAMES[index]) return null;
  return <span className="whitespace-nowrap rounded-md bg-maku-50 px-2 py-0.5 text-xs font-medium text-maku-700">{INDEX_NAMES[index]}</span>;
}

export function Avatar({ name, url }: { name: string; url: string | null }) {
  if (url) return <img src={url} alt={name} className="h-14 w-14 rounded-full object-cover" />;
  const initials = name.split(" ").map((p) => p[0]).slice(0, 2).join("");
  return <div className="flex h-14 w-14 items-center justify-center rounded-full bg-maku-100 text-lg font-semibold text-maku-700">{initials}</div>;
}
