// Backend sözleşmesi: backend/app/models/schemas.py ile birebir aynı tutulmalıdır.

export type Decision = "accepted" | "rejected" | "manual_check";

export interface AuthorCandidate {
  scholar_id: string;
  name: string;
  affiliation: string | null;
  email_domain: string | null;
  photo_url: string | null;
  cited_by_total: number | null;
  interests: string[];
}

export interface JournalInfo {
  title: string;
  issn: string | null;
  indexes: string[];
}

export interface Publication {
  id: string;
  title: string;
  authors: string[];
  year: number | null;
  online_year: number | null;
  venue: string | null;
  doi: string | null;
  work_type: string;
  journal: JournalInfo | null;
}

export interface EvidenceItem {
  order: number;
  kind: string;
  label: string;
  highlight_terms: string[];
}

export interface Evaluation {
  decision: Decision;
  reasons: string[];
  index: string;
  evidence_plan: EvidenceItem[];
}

export interface PublicationRow {
  publication: Publication;
  evaluation: Evaluation;
}

export interface CitationRow {
  citing: Publication;
  cited: Publication;
  evaluation: Evaluation;
}

export interface YearOption {
  data_year: number;
  application_year: number;
  label: string;
  recommended: boolean;
  hint: string;
}

export type JobKind = "articles" | "citations";

export interface JobStatus {
  job_id: string;
  state: string;
  progress: number;
  message: string | null;
  output_files: string[];
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...init });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `İstek başarısız (${res.status})`);
  }
  return res.json();
}

const q = (params: Record<string, string | number>) =>
  new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString();

export const api = {
  searchAuthors: (name: string) => request<AuthorCandidate[]>(`/api/authors/search?${q({ name })}`),
  years: () => request<YearOption[]>("/api/years"),
  publications: (id: string, year: number) =>
    request<PublicationRow[]>(`/api/authors/${id}/publications?${q({ year })}`),
  citations: (id: string, year: number, author_name: string) =>
    request<CitationRow[]>(`/api/authors/${id}/citations?${q({ year, author_name })}`),
  createJob: (body: { kind: JobKind; scholar_id: string; author_name: string; data_year: number; item_ids: string[] }) =>
    request<JobStatus>("/api/jobs", { method: "POST", body: JSON.stringify(body) }),
  job: (id: string) => request<JobStatus>(`/api/jobs/${id}`),
};
