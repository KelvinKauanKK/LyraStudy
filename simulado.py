import clock
import os
from datetime import date
from tkinter import filedialog
import customtkinter as ctk
import exam
from rules import build_schedule, weekly_minutes, analyze, last3
from storage import save
from theme import PRIMARY, RED, MUTED, TEAL

def num(e):
    try: return float(e.get().strip().replace(",", "."))
    except ValueError: return None

class SimuladoDialog(ctk.CTkToplevel):
    """Registro de simulado. Passo 1: nome da prova, máximo de questões e matérias. Passo 2: números POR MATÉRIA (questões, acertos, anuladas,
    peso) — o total de acertos é a SOMA automática. A soma das questões das matérias tem de ser igual ao máximo da prova."""
    def __init__(self, master, app, on_done):
        super().__init__(master); self.title("Registrar simulado"); self.geometry("860x720")
        self.transient(master.winfo_toplevel()); self.after(150, self.grab_set)
        self.app, self.on_done, self.new, self.vars, self.files, self.rows, self.wcells = app, on_done, [], {}, [], [], []
        self.step1()

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def check(self, n, on=False):
        v = self.vars.setdefault(n, ctk.BooleanVar(value=on))
        ctk.CTkCheckBox(self.box, text=n, variable=v).pack(anchor="w", pady=3)

    # ---------- passo 1 ----------
    def step1(self):
        self.clear()
        ctk.CTkLabel(self, text="Dados da prova", font=("Segoe UI", 18, "bold")).pack(pady=(16, 8))
        r = ctk.CTkFrame(self, fg_color="transparent"); r.pack()
        self.e_name = ctk.CTkEntry(r, width=330, placeholder_text="Nome da prova (ex.: ITA 2025, EFOMM 1º Dia)"); self.e_name.grid(row=0, column=0, padx=6)
        self.e_max = ctk.CTkEntry(r, width=210, placeholder_text="Máximo de questões da prova"); self.e_max.grid(row=0, column=1, padx=6)
        ctk.CTkLabel(self, text="Quais matérias caíram neste simulado?").pack(pady=(14, 2))
        self.box = ctk.CTkScrollableFrame(self, height=240); self.box.pack(fill="x", padx=24)
        for n in self.app.data["subjects"]: self.check(n)
        for n in self.new: self.check(n, True)
        r2 = ctk.CTkFrame(self, fg_color="transparent"); r2.pack(pady=8)
        self.e_new = ctk.CTkEntry(r2, width=240, placeholder_text="Matéria que não está na lista"); self.e_new.pack(side="left")
        ctk.CTkButton(r2, text="➕ Adicionar", width=100, command=self.add_new).pack(side="left", padx=6)
        self.err = ctk.CTkLabel(self, text="", text_color=RED); self.err.pack()
        ctk.CTkButton(self, text="Continuar", command=self.step2, **PRIMARY).pack(pady=8)

    def add_new(self):
        n = self.e_new.get().strip()
        if not n: return
        if n.lower() in (x.lower() for x in [*self.app.data["subjects"], *self.new]): return self.err.configure(text="Essa matéria já está na lista.")
        self.new.append(n); self.check(n, True); self.e_new.delete(0, "end"); self.err.configure(text="")

    # ---------- passo 2 ----------
    def step2(self):
        name, mx = self.e_name.get().strip(), self.e_max.get().strip(); sel = [n for n, v in self.vars.items() if v.get()]
        if not name: return self.err.configure(text="Informe o nome da prova.")
        if not mx.isdigit() or int(mx) < 1: return self.err.configure(text="O máximo de questões deve ser um número inteiro maior que zero.")
        if not sel: return self.err.configure(text="Selecione ao menos uma matéria.")
        self.name, self.max_q, self.sel = name, int(mx), sel; self.clear()
        ctk.CTkLabel(self, text=f"{name} — máx. {self.max_q} questões", font=("Segoe UI", 17, "bold")).pack(pady=(14, 0))
        ctk.CTkLabel(self, text="Preencha por matéria. O total de acertos da prova é a soma automática dos acertos de cada matéria.", text_color=MUTED).pack()
        box = ctk.CTkScrollableFrame(self); box.pack(fill="both", expand=True, padx=16, pady=8)
        heads = ["Matéria", "Questões", "Acertos", "Anuladas", "Das anuladas,\nacertei", "Peso", "Resultado"]
        for c, h in enumerate(heads):
            lbl = ctk.CTkLabel(box, text=h, text_color=MUTED); lbl.grid(row=0, column=c, padx=4, pady=2)
            if c == 5: self.wcells.append(lbl)
        base, extra = divmod(self.max_q, len(sel)); self.rows = []
        for i, n in enumerate(sel):
            row = {"s": n, "touched": False, "t": ctk.StringVar(value=str(base + (1 if i < extra else 0))), "h": ctk.StringVar(value="0"), "a": ctk.StringVar(value="0"),
                   "ah": ctk.StringVar(value="0"), "w": ctk.StringVar(value="1")}
            ctk.CTkLabel(box, text=n, anchor="w", width=150).grid(row=i + 1, column=0, padx=4, pady=3, sticky="w")
            for c, k in ((1, "t"), (2, "h"), (3, "a"), (4, "ah"), (5, "w")):
                e = ctk.CTkEntry(box, width=70, textvariable=row[k]); e.grid(row=i + 1, column=c, padx=4, pady=3)
                if k == "ah": e.bind("<Key>", lambda ev, r=row: r.__setitem__("touched", True))
                if k == "w": self.wcells.append(e)
                row[k + "_e"] = e
            row["res"] = ctk.CTkLabel(box, text="—", width=170, anchor="w"); row["res"].grid(row=i + 1, column=6, padx=4)
            for k in ("t", "h", "a", "ah", "w"): row[k].trace_add("write", lambda *a, r=row, k=k: self.on_edit(r, k))
            self.rows.append(row)
        self.sum_lbl = ctk.CTkLabel(self, text="", font=("Segoe UI", 13, "bold")); self.sum_lbl.pack(pady=(2, 0))
        self.sw = ctk.CTkSwitch(self, text="A prova possui pesos diferentes por matéria?", command=self.toggle_weights); self.sw.pack(pady=4)
        self.tot_lbl = ctk.CTkLabel(self, text="", text_color=TEAL); self.tot_lbl.pack()
        att = ctk.CTkFrame(self, fg_color="transparent"); att.pack(fill="x", padx=18, pady=4)
        ctk.CTkButton(att, text="📎 Anexar arquivos (PDF, imagens, redações…)", fg_color="gray30", command=self.pick_files).pack(side="left")
        self.att_lbl = ctk.CTkLabel(att, text="", text_color=MUTED); self.att_lbl.pack(side="left", padx=10)
        self.err = ctk.CTkLabel(self, text="", text_color=RED, wraplength=780); self.err.pack()
        ctk.CTkButton(self, text="Salvar simulado", command=self.save_sim, **PRIMARY).pack(pady=8)
        self.toggle_weights(); self.recalc()

    def weighted(self): return bool(self.sw.get())
    def toggle_weights(self):
        for w in self.wcells: (w.grid() if self.weighted() else w.grid_remove())
        self.recalc()
    def on_edit(self, row, k):
        if k == "a" and not row["touched"]: row["ah"].set(row["a"].get())       # padrão: as anuladas contam como acerto (abatimento do exemplo)
        self.recalc()
    def pick_files(self):
        got = filedialog.askopenfilenames(title="Anexar ao simulado", filetypes=[("Documentos e imagens", "*.pdf *.png *.jpg *.jpeg *.gif *.bmp *.webp *.doc *.docx *.txt"), ("Todos os arquivos", "*.*")])
        for f in got:
            if f not in self.files: self.files.append(f)
        self.att_lbl.configure(text=f"{len(self.files)} arquivo(s) anexado(s): " + ", ".join(os.path.basename(f) for f in self.files[:3]) + ("…" if len(self.files) > 3 else ""))

    def read(self, r):
        """(questões, acertos, anuladas, anuladas acertadas) como inteiros; None se algum campo for inválido."""
        try: return tuple(int(r[k].get().strip()) for k in ("t", "h", "a", "ah"))
        except ValueError: return None

    def recalc(self):
        """Atualiza a soma das questões (precisa ser = máximo), o resultado de cada matéria (com anuladas) e o total de acertos automático."""
        soma, H, T, ok = 0, 0, 0, True
        for r in self.rows:
            v = self.read(r)
            if not v: r["res"].configure(text="—"); ok = False; continue
            t, h, a, ah = v; soma += t
            if t < 1 or not 0 <= h <= t or not 0 <= a <= t or not 0 <= ah <= min(a, h): r["res"].configure(text="⚠ confira os números", text_color=RED); ok = False; continue
            eh, et = exam.adjust(t, h, a, ah); H, T = H + eh, T + et
            r["res"].configure(text=(f"{eh} de {et}  •  nota {eh / et * 10:.1f}" if et else "tudo anulado"), text_color=TEAL if et else RED)
        good = soma == self.max_q
        self.sum_lbl.configure(text=f"Soma das questões: {soma} / {self.max_q}" + ("  ✔" if good else "  — precisa ser igual ao máximo da prova"), text_color=TEAL if good else RED)
        self.tot_lbl.configure(text=f"Total de acertos da prova (automático): {H} de {T}" + (f"  •  nota geral {H / T * 10:.1f}" if T and ok and not self.weighted() else ""))

    def save_sim(self):
        rows = []
        for r in self.rows:
            v = self.read(r)
            if not v: return self.err.configure(text=f"{r['s']}: use apenas números inteiros nos campos de questões, acertos e anuladas.")
            try: w = float(r["w"].get().replace(",", ".")) if self.weighted() else 1.0
            except ValueError: return self.err.configure(text=f"{r['s']}: peso inválido.")
            rows.append({"subject": r["s"], "total": v[0], "hits": v[1], "annulled": v[2], "annulled_hit": v[3], "weight": w})
        d = self.app.data
        try: cy = self.app.city_widget().city.year()
        except Exception: cy = 0
        try: rec = exam.compute_exam(self.name, self.max_q, rows, self.weighted(), cy)
        except ValueError as e: return self.err.configure(text=str(e))
        rec["attachments"] = exam.add_attachments(rec["id"], self.files) if self.files else []
        added = False
        for n in rec["subjects"]:
            if n not in d["subjects"]: d["subjects"][n] = 3; added = True      # matéria nova entra com dificuldade 3
        if added: d["schedule"] = build_schedule(d["subjects"], d["daily_goal_h"], d["per_day"])
        d["simulados"].append(rec); save(d); self.destroy(); self.on_done()

class WeightsDialog(ctk.CTkToplevel):
    """Revisão manual dos graus de dificuldade (1 a 5)."""
    def __init__(self, master, app):
        super().__init__(master); self.title("Graus de dificuldade"); self.geometry("460x460")
        self.transient(master.winfo_toplevel()); self.after(150, self.grab_set)
        ctk.CTkLabel(self, text="Dificuldade (1 = fácil, 5 = muito difícil)", font=("Segoe UI", 15, "bold")).pack(pady=12)
        box = ctk.CTkScrollableFrame(self); box.pack(fill="both", expand=True, padx=20)
        self.sl = {}
        for s, w in app.data["subjects"].items():
            r = ctk.CTkFrame(box, fg_color="transparent"); r.pack(fill="x", pady=6)
            ctk.CTkLabel(r, text=s, width=130, anchor="w").pack(side="left")
            v = ctk.CTkLabel(r, text=str(max(1, min(5, int(w)))), width=24)
            sl = ctk.CTkSlider(r, from_=1, to=5, number_of_steps=4, command=lambda x, l=v: l.configure(text=str(int(round(x)))))
            sl.set(max(1, min(5, int(w)))); sl.pack(side="left", fill="x", expand=True, padx=8); v.pack(side="left"); self.sl[s] = sl

        def ok():
            d = app.data
            d["subjects"] = {s: int(round(x.get())) for s, x in self.sl.items()}
            d["schedule"] = build_schedule(d["subjects"], d["daily_goal_h"], d["per_day"])
            d["schedule_date"] = clock.today().isoformat(); save(d); self.destroy(); app.refresh()
        ctk.CTkButton(self, text="Salvar e refazer cronograma", command=ok, **PRIMARY).pack(pady=12)

class ProposalDialog(ctk.CTkToplevel):
    """Nova grade calculada só com os últimos 3 simulados. Aceitar grava no cronograma."""
    def __init__(self, master, app, new, changes, sched):
        super().__init__(master); self.title("Reajuste do cronograma"); self.geometry("560x540")
        self.transient(master.winfo_toplevel()); self.after(150, self.grab_set)
        d = app.data; sims = last3(d)
        old_m, new_m = weekly_minutes(d["subjects"], d["daily_goal_h"]), weekly_minutes(new, d["daily_goal_h"])
        weak = [r["subject"] for r in analyze(d) if r["avg"] < 6]
        ctk.CTkLabel(self, text="Reajuste do cronograma", font=("Segoe UI", 18, "bold")).pack(pady=(16, 2))
        ctk.CTkLabel(self, text=f"Baseado estritamente nos últimos {len(sims)} simulado(s): "
                     + ", ".join(f"{x['date'][8:10]}/{x['date'][5:7]}" for x in sims), text_color=MUTED, wraplength=500).pack()
        ctk.CTkLabel(self, text="🎯 Pior desempenho: " + (", ".join(weak) or "nenhum"), wraplength=500).pack(pady=4)
        box = ctk.CTkScrollableFrame(self); box.pack(fill="both", expand=True, padx=16, pady=8)
        for s, o, n, avg, dl, wn in changes:
            ctk.CTkLabel(box, anchor="w", justify="left", text=(
                f"{'🔺' if n > o else '🔻'} {s}: dificuldade {o} → {n}\n    nota média {avg:.1f}/10 ({dl:+.1f}) • peso da prova ×{wn:.1f} • "
                f"{old_m.get(s, 0)} → {new_m.get(s, 0)} min/semana")).pack(fill="x", pady=4)

        def close(accept):
            if accept: d.update(subjects=new, schedule=sched)
            save(d); self.destroy(); app.refresh()
        ctk.CTkLabel(self, text="Aceita a Nova Grade?", font=("Segoe UI", 15, "bold")).pack(pady=(4, 4))
        b = ctk.CTkFrame(self, fg_color="transparent"); b.pack(pady=10)
        ctk.CTkButton(b, text="Aceita a Nova Grade", command=lambda: close(True), **PRIMARY).pack(side="left", padx=6)
        ctk.CTkButton(b, text="Manter a atual", fg_color="gray30", command=lambda: close(False)).pack(side="left", padx=6)
