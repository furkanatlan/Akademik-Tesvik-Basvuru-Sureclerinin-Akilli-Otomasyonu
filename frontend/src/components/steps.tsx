import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BookOpenText, Building2, CalendarCheck, Loader2, Mail, Quote, Search, Star } from "lucide-react";
import { api, type AuthorCandidate, type JobKind, type YearOption } from "../lib/api";
import { Avatar, Card } from "./ui";

// ------------------------------------------------------------------ 1. Akademisyen seçimi
export function AuthorStep({ onSelect }: { onSelect: (a: AuthorCandidate) => void }) {
  const [input, setInput] = useState("");
  const [term, setTerm] = useState("");
  const { data, isFetching, error } = useQuery({
    queryKey: ["authors", term],
    queryFn: () => api.searchAuthors(term),
    enabled: term.length >= 3,
  });
  // Tek sonuç geldiyse seçim ekranı atlanır
  useEffect(() => {
    if (data?.length === 1) onSelect(data[0]);
  }, [data, onSelect]);

  return (
    <Card>
      <h2 className="text-xl font-semibold text-slate-900">Adınızı ve soyadınızı yazın</h2>
      <p className="mt-1 text-sm text-slate-600">Google Scholar profiliniz aranacak. Aynı isimde birden fazla akademisyen varsa kendinizi seçeceksiniz.</p>
      <form
        className="mt-5 flex flex-col gap-3 sm:flex-row"
        onSubmit={(e) => {
          e.preventDefault();
          setTerm(input.trim());
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="ör. Ahmet Yılmaz"
          className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-maku-500 focus:ring-2 focus:ring-maku-100"
        />
        <button
          disabled={input.trim().length < 3 || isFetching}
          className="flex items-center justify-center gap-2 rounded-xl bg-maku-500 px-6 py-3 font-semibold text-white hover:bg-maku-600 disabled:opacity-50"
        >
          {isFetching ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />} Ara
        </button>
      </form>

      {error && <p className="mt-4 text-sm text-rose-700">{(error as Error).message}</p>}
      {data && data.length === 0 && <p className="mt-4 text-sm text-slate-600">Sonuç bulunamadı. Adınızı Scholar profilinizdeki gibi yazmayı deneyin.</p>}
      {data && data.length > 1 && (
        <p className="mt-5 rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-900">
          <b>{data.length}</b> akademisyen bulundu. Kurum bilgisine bakarak kendinizi seçin.
        </p>
      )}
      <div className="mt-4 grid gap-3">
        {data?.map((a) => (
          <button
            key={a.scholar_id}
            onClick={() => onSelect(a)}
            className="flex items-center gap-4 rounded-xl border border-slate-200 p-4 text-left transition hover:border-maku-500 hover:bg-maku-50"
          >
            <Avatar name={a.name} url={a.photo_url} />
            <div className="min-w-0 flex-1">
              <div className="font-semibold text-slate-900">{a.name}</div>
              {a.affiliation && <div className="flex items-center gap-1.5 text-sm text-slate-700"><Building2 size={14} /> {a.affiliation}</div>}
              {a.email_domain && <div className="flex items-center gap-1.5 text-xs text-slate-500"><Mail size={12} /> {a.email_domain} adresinde doğrulanmış e-posta</div>}
              {a.interests.length > 0 && <div className="mt-1 truncate text-xs text-slate-500">{a.interests.join(" · ")}</div>}
            </div>
            {a.cited_by_total != null && (
              <div className="text-right text-xs text-slate-500">
                <div className="text-lg font-semibold text-slate-800">{a.cited_by_total}</div>atıf
              </div>
            )}
          </button>
        ))}
      </div>
    </Card>
  );
}

// ------------------------------------------------------------------ 2. İşlem seçimi
export function ActionStep({ onSelect }: { onSelect: (k: JobKind) => void }) {
  const options: { kind: JobKind; title: string; desc: string; icon: JSX.Element }[] = [
    {
      kind: "articles",
      title: "Makale belgelerini hazırla",
      desc: "Seçilen yılda yayımlanan makaleleriniz: ilk sayfa (tarih + adınız işaretli) ve derginin tarandığı dizin belgeleri tek PDF'te.",
      icon: <BookOpenText size={28} />,
    },
    {
      kind: "citations",
      title: "Atıf belgelerini hazırla",
      desc: "Eski yayınlarınız dahil, seçilen yılda aldığınız atıflar: atıf yapan makalenin kaynakçası, ilk sayfası ve dizin belgesi.",
      icon: <Quote size={28} />,
    },
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {options.map((o) => (
        <button key={o.kind} onClick={() => onSelect(o.kind)} className="text-left">
          <Card className="h-full transition hover:border-maku-500 hover:shadow-md">
            <div className="text-maku-500">{o.icon}</div>
            <h3 className="mt-3 text-lg font-semibold text-slate-900">{o.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{o.desc}</p>
          </Card>
        </button>
      ))}
    </div>
  );
}

// ------------------------------------------------------------------ 3. Yıl seçimi
export function YearStep({ onSelect }: { onSelect: (y: YearOption) => void }) {
  const { data } = useQuery({ queryKey: ["years"], queryFn: api.years });
  return (
    <Card>
      <h2 className="text-xl font-semibold text-slate-900">Hangi yılın belgelerini hazırlıyorsunuz?</h2>
      <p className="mt-1 text-sm text-slate-600">
        Teşvik başvurusu, <b>bir önceki yılın</b> yayın ve atıfları için yapılır. Yalnızca seçtiğiniz yıla ait kayıtlar listelenir; eski yıllar dikkate alınmaz.
      </p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {data?.map((o) => (
          <button
            key={o.data_year}
            onClick={() => onSelect(o)}
            className={`relative rounded-xl border-2 p-5 text-left transition hover:border-maku-500 ${o.recommended ? "border-maku-500 bg-maku-50" : "border-slate-200"}`}
          >
            {o.recommended && (
              <span className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-maku-500 px-2 py-0.5 text-xs font-semibold text-white">
                <Star size={12} /> Önerilen
              </span>
            )}
            <CalendarCheck className="text-maku-500" />
            <div className="mt-2 text-3xl font-bold text-slate-900">{o.data_year}</div>
            <div className="text-sm font-medium text-slate-700">yılı yayın ve atıfları</div>
            <div className="mt-1 text-sm text-maku-700">→ {o.application_year} yılı başvurusu</div>
            <p className="mt-3 text-xs text-slate-500">{o.hint}</p>
          </button>
        ))}
      </div>
    </Card>
  );
}
