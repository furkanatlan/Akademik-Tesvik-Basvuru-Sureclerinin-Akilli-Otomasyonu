import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, CircleAlert, Database, Loader2, LogIn, RefreshCw } from "lucide-react";
import { api, type DbKey, type DbStatus } from "../lib/api";
import { Card } from "./ui";

const DB_INFO: Record<DbKey, { title: string; uses: string }> = {
  wos: {
    title: "Web of Science",
    uses: "SCI-Expanded / SSCI / AHCI atıf listeleri ve dergi dizin kanıtları",
  },
  scopus: {
    title: "Scopus",
    uses: "Scopus atıf listeleri ve derginin Scopus kapsamı kanıtı",
  },
};

/** WoS / Scopus girişi: kullanıcı, sistemin yönettiği gömülü tarayıcıda kurum hesabıyla oturum açar.
 *  En az bir veri tabanında giriş doğrulanmadan dizin taraması ve kanıt üretimi başlamaz. */
export function DbLoginStep({ onDone }: { onDone: () => void }) {
  const qc = useQueryClient();
  const { data, error } = useQuery({ queryKey: ["db-session"], queryFn: api.dbOverview, refetchInterval: 15_000 });
  const [active, setActive] = useState<DbKey | null>(null);
  const refresh = () => qc.invalidateQueries({ queryKey: ["db-session"] });

  const open = useMutation({
    mutationFn: (db: DbKey) => api.dbOpen(db),
    onSuccess: (_, db) => setActive(db),
  });
  const check = useMutation({ mutationFn: api.dbCheck, onSettled: refresh });
  const confirm = useMutation({ mutationFn: api.dbConfirm, onSettled: refresh });
  const logout = useMutation({ mutationFn: api.dbLogout, onSettled: refresh });

  if (error) return <Card className="text-rose-700">{(error as Error).message}</Card>;
  if (!data)
    return (
      <Card className="flex items-center gap-3 text-slate-600">
        <Loader2 className="animate-spin" /> Tarayıcı hazırlanıyor...
      </Card>
    );

  const anyLoggedIn = data.databases.some((d) => d.logged_in);
  const canContinue = anyLoggedIn || !data.login_required;
  const lastCheck = check.data ?? confirm.data;

  return (
    <div className="space-y-4">
      <Card>
        <h2 className="text-xl font-semibold text-slate-900">Web of Science / Scopus girişi</h2>
        <p className="mt-1 text-sm text-slate-600">
          Dizin taraması ve kılavuzdaki atıf listeleri bu veri tabanlarından alınır. Aşağıdan <b>Giriş yap</b>'a basın; açılan
          tarayıcıda <b>"Institutional Sign In"</b> bölümünden üniversitenizi seçip kurum hesabınızla giriş yapın. Kampüs ağındaysanız
          giriş istenmeden erişim açılabilir. Şifreniz bu uygulamaya kaydedilmez; oturum yalnızca bu bilgisayardaki tarayıcıda kalır.
        </p>
        {!data.browser_ready && (
          <p className="mt-3 rounded-lg bg-rose-50 px-4 py-2 text-sm text-rose-800">
            Gömülü tarayıcı çalışmıyor. <code>docker compose up -d browser</code> komutunu çalıştırın.
          </p>
        )}

        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {data.databases.map((d) => (
            <DbCard
              key={d.database}
              status={d}
              busy={open.isPending || check.isPending}
              onOpen={() => open.mutate(d.database)}
              onCheck={() => {
                setActive(d.database);
                check.mutate(d.database);
              }}
              onLogout={() => logout.mutate(d.database)}
            />
          ))}
        </div>
      </Card>

      {active && (
        <Card padded={false} className="overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-slate-100 px-5 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm">
              <span className="font-semibold text-slate-900">{DB_INFO[active].title}</span>
              <span className="text-slate-500"> — giriş yaptıktan sonra "Girişi kontrol et"e basın</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => check.mutate(active)}
                className="flex items-center gap-1.5 rounded-lg bg-maku-500 px-3 py-2 text-sm font-semibold text-white hover:bg-maku-600"
              >
                {check.isPending ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />} Girişi kontrol et
              </button>
              {lastCheck && !lastCheck.logged_in && (
                <button
                  onClick={() => confirm.mutate(active)}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
                >
                  Girişi yaptım, onaylıyorum
                </button>
              )}
            </div>
          </div>
          {lastCheck && (
            <p className={`px-5 py-2 text-sm ${lastCheck.logged_in ? "bg-emerald-50 text-emerald-800" : "bg-amber-50 text-amber-900"}`}>
              {lastCheck.detail}
            </p>
          )}
          <iframe
            title="Gömülü tarayıcı"
            src={`${data.novnc_url}/vnc.html?autoconnect=1&resize=scale&reconnect=1&show_dot=1`}
            className="h-[560px] w-full bg-slate-900 sm:h-[640px]"
          />
        </Card>
      )}

      <Card className="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-600">
          {anyLoggedIn
            ? "Giriş doğrulandı. Dizin taraması ve kanıt hazırlığına geçebilirsiniz."
            : data.login_required
              ? "Devam etmek için en az bir veri tabanında giriş yapılmalı."
              : "Geliştirici (mock) modu: giriş yapmadan devam edebilirsiniz."}
        </p>
        <button
          disabled={!canContinue}
          onClick={onDone}
          className="flex items-center gap-2 rounded-xl bg-maku-500 px-5 py-3 font-semibold text-white hover:bg-maku-600 disabled:opacity-50"
        >
          Taramaya geç <ArrowRight size={18} />
        </button>
      </Card>
    </div>
  );
}

function DbCard(props: { status: DbStatus; busy: boolean; onOpen: () => void; onCheck: () => void; onLogout: () => void }) {
  const { status: s } = props;
  const info = DB_INFO[s.database];
  return (
    <div className={`rounded-xl border-2 p-4 ${s.logged_in ? "border-emerald-400 bg-emerald-50/50" : "border-slate-200"}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-semibold text-slate-900">
          <Database size={18} className="text-maku-500" /> {info.title}
        </div>
        {s.logged_in ? (
          <span className="flex items-center gap-1 text-xs font-semibold text-emerald-700">
            <CheckCircle2 size={14} /> Giriş yapıldı
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs font-semibold text-slate-500">
            <CircleAlert size={14} /> Giriş yok
          </span>
        )}
      </div>
      <p className="mt-1 text-xs text-slate-500">{info.uses}</p>
      <div className="mt-3 flex gap-2">
        {s.logged_in ? (
          <button onClick={props.onLogout} className="text-xs font-medium text-slate-500 underline">
            Oturumu unut
          </button>
        ) : (
          <>
            <button
              disabled={props.busy}
              onClick={props.onOpen}
              className="flex items-center gap-1.5 rounded-lg bg-maku-500 px-3 py-1.5 text-sm font-semibold text-white hover:bg-maku-600 disabled:opacity-50"
            >
              <LogIn size={15} /> Giriş yap
            </button>
            <button onClick={props.onCheck} className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100">
              Kontrol et
            </button>
          </>
        )}
      </div>
    </div>
  );
}
