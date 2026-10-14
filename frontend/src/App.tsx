import { useState } from "react";
import { ArrowLeft, GraduationCap } from "lucide-react";
import type { AuthorCandidate, JobKind, YearOption } from "./lib/api";
import { Stepper } from "./components/ui";
import { ActionStep, AuthorStep, YearStep } from "./components/steps";
import { ResultsStep } from "./components/ResultsStep";

export default function App() {
  const [author, setAuthor] = useState<AuthorCandidate | null>(null);
  const [kind, setKind] = useState<JobKind | null>(null);
  const [year, setYear] = useState<YearOption | null>(null);

  const step = !author ? 0 : !kind ? 1 : !year ? 2 : 3;
  const back = () => (year ? setYear(null) : kind ? setKind(null) : setAuthor(null));

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-8 flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-maku-500 p-2 text-white">
            <GraduationCap />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Akademik Teşvik Asistanı</h1>
            <p className="text-xs text-slate-500">Yayın ve atıf belgelerini kılavuza uygun hazırlar</p>
          </div>
        </div>
        <Stepper current={step} />
      </header>

      {author && (
        <div className="mb-4 flex flex-wrap items-center gap-2 text-sm">
          <button onClick={back} className="flex items-center gap-1 rounded-lg px-2 py-1 text-slate-600 hover:bg-slate-200">
            <ArrowLeft size={16} /> Geri
          </button>
          <span className="rounded-full bg-white px-3 py-1 shadow-sm">{author.name} · {author.affiliation}</span>
          {kind && <span className="rounded-full bg-white px-3 py-1 shadow-sm">{kind === "articles" ? "Makaleler" : "Atıflar"}</span>}
          {year && <span className="rounded-full bg-white px-3 py-1 shadow-sm">{year.data_year} → {year.application_year} başvurusu</span>}
        </div>
      )}

      {step === 0 && <AuthorStep onSelect={setAuthor} />}
      {step === 1 && <ActionStep onSelect={setKind} />}
      {step === 2 && <YearStep onSelect={setYear} />}
      {step === 3 && author && kind && year && <ResultsStep author={author} kind={kind} year={year} />}
    </div>
  );
}
