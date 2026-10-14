import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ChevronDown, FileDown, Loader2 } from "lucide-react";
import { api, type AuthorCandidate, type Evaluation, type JobKind, type Publication, type YearOption } from "../lib/api";
import { Card, DecisionBadge, IndexBadge } from "./ui";

interface Row {
  id: string;
  title: string;
  subtitle: string;
  group?: string; // atıflarda: atıf alan yayın
  evaluation: Evaluation;
}

const venue = (p: Publication) => [p.journal?.title ?? p.venue, p.year].filter(Boolean).join(" · ");

export function ResultsStep({ author, kind, year }: { author: AuthorCandidate; kind: JobKind; year: YearOption }) {
  const { data: rows, isLoading, error } = useQuery({
    queryKey: [kind, author.scholar_id, year.data_year],
    queryFn: async (): Promise<Row[]> => {
      if (kind === "articles") {
        const res = await api.publications(author.scholar_id, year.data_year);
        return res.map((r) => ({ id: r.publication.id, title: r.publication.title, subtitle: venue(r.publication), evaluation: r.evaluation }));
      }
      const res = await api.citations(author.scholar_id, year.data_year, author.name);
      return res.map((r) => ({
        id: r.citing.id,
        title: r.citing.title,
        subtitle: `${r.citing.authors.join(", ")} — ${venue(r.citing)}`,
        group: r.cited.title,
        evaluation: r.evaluation,
      }));
    },
  });

  const [selected, setSelected] = useState<Set<string>>(new Set());
  useEffect(() => {
    if (rows) setSelected(new Set(rows.filter((r) => r.evaluation.decision === "accepted").map((r) => r.id)));
  }, [rows]);

  const counts = useMemo(() => {
    const c = { accepted: 0, rejected: 0, manual_check: 0 };
    rows?.forEach((r) => c[r.evaluation.decision]++);
    return c;
  }, [rows]);

  const job = useMutation({
    mutationFn: () =>
      api.createJob({ kind, scholar_id: author.scholar_id, author_name: author.name, data_year: year.data_year, item_ids: [...selected] }),
  });

  if (isLoading)
    return (
      <Card className="flex items-center gap-3 text-slate-600">
        <Loader2 className="animate-spin" /> {kind === "articles" ? "Yayınlar" : "Atıflar"} taranıyor... (gerçek modda birkaç dakika sürebilir)
      </Card>
    );
  if (error) return <Card className="text-rose-700">{(error as Error).message}</Card>;
  if (!rows?.length)
    return <Card>{year.data_year} yılına ait {kind === "articles" ? "yayın" : "atıf"} bulunamadı.</Card>;

  const groups = [...new Set(rows.map((r) => r.group ?? ""))];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <Stat label="Kabul" value={counts.accepted} cls="text-emerald-700" />
        <Stat label="Kontrol gerekli" value={counts.manual_check} cls="text-amber-700" />
        <Stat label="Kabul edilmez" value={counts.rejected} cls="text-rose-700" />
      </div>

      {groups.map((g) => (
        <Card key={g} padded={false} className="overflow-hidden">
          {g && (
            <div className="border-b border-slate-100 px-5 py-3 text-sm">
              <span className="text-slate-500">Atıf alan yayınınız: </span>
              <span className="font-medium text-slate-900">{g}</span>
            </div>
          )}
          <ul className="divide-y divide-slate-100">
            {rows.filter((r) => (r.group ?? "") === g).map((r) => (
              <ResultRow
                key={r.id}
                row={r}
                checked={selected.has(r.id)}
                onToggle={() => {
                  const s = new Set(selected);
                  s.has(r.id) ? s.delete(r.id) : s.add(r.id);
                  setSelected(s);
                }}
              />
            ))}
          </ul>
        </Card>
      ))}

      <Card className="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-sm text-slate-600">
          <b>{selected.size}</b> kayıt için kılavuza uygun belge dosyası hazırlanacak (her kayıt tek PDF).
        </div>
        <button
          disabled={!selected.size || job.isPending}
          onClick={() => job.mutate()}
          className="flex items-center gap-2 rounded-xl bg-maku-500 px-5 py-3 font-semibold text-white hover:bg-maku-600 disabled:opacity-50"
        >
          <FileDown size={18} /> Belgeleri hazırla
        </button>
      </Card>
      {job.data && <JobProgress jobId={job.data.job_id} />}
    </div>
  );
}

function Stat({ label, value, cls }: { label: string; value: number; cls: string }) {
  return (
    <Card padded={false} className="p-4 text-center">
      <div className={`text-2xl font-bold ${cls}`}>{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </Card>
  );
}

function ResultRow({ row, checked, onToggle }: { row: Row; checked: boolean; onToggle: () => void }) {
  const [open, setOpen] = useState(false);
  const { evaluation: ev } = row;
  return (
    <li className="px-5 py-4">
      <div className="flex items-start gap-3">
        <input type="checkbox" className="mt-1 h-4 w-4 accent-maku-500" checked={checked} disabled={ev.decision === "rejected"} onChange={onToggle} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-slate-900">{row.title}</span>
            <IndexBadge index={ev.index} />
          </div>
          <div className="mt-0.5 text-sm text-slate-500">{row.subtitle}</div>
          {ev.reasons.map((r) => (
            <div key={r} className="mt-1 text-sm text-slate-700">• {r}</div>
          ))}
          {ev.evidence_plan.length > 0 && (
            <button onClick={() => setOpen(!open)} className="mt-2 flex items-center gap-1 text-sm font-medium text-maku-600">
              Hazırlanacak belgeler ({ev.evidence_plan.length}) <ChevronDown size={16} className={open ? "rotate-180" : ""} />
            </button>
          )}
          {open && (
            <ol className="mt-2 space-y-1 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
              {ev.evidence_plan.map((e) => (
                <li key={e.order}>
                  <b>{e.order}.</b> {e.label}
                </li>
              ))}
            </ol>
          )}
        </div>
        <DecisionBadge decision={ev.decision} />
      </div>
    </li>
  );
}

function JobProgress({ jobId }: { jobId: string }) {
  const { data } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.job(jobId),
    refetchInterval: (q) => (["SUCCESS", "FAILURE"].includes(q.state.data?.state ?? "") ? false : 2000),
  });
  if (!data) return null;
  const failed = data.state === "FAILURE";
  return (
    <Card>
      <div className="mb-2 flex justify-between text-sm">
        <span className="font-medium">{failed ? "Hata" : data.state === "SUCCESS" ? "Tamamlandı" : "Hazırlanıyor..."}</span>
        <span>{data.progress}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full ${failed ? "bg-rose-500" : "bg-maku-500"}`} style={{ width: `${failed ? 100 : data.progress}%` }} />
      </div>
      {data.message && <p className={`mt-2 text-sm ${failed ? "text-rose-700" : "text-slate-600"}`}>{data.message}</p>}
      {data.output_files.map((f) => (
        <a key={f} href={`/api/files/${encodeURIComponent(f)}`} className="mt-2 block text-sm font-medium text-maku-600 underline">
          {f}
        </a>
      ))}
    </Card>
  );
}
