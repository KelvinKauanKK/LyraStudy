"""Visão "Simulados": indicadores, evolução, BUSCA por nome, PAGINAÇÃO (10 por aba) e anexos de cada simulado."""
from datetime import date
from tkinter import filedialog, messagebox
import customtkinter as ctk
import exam
from library import open_file
from rules import overall, sub_scores, level
from storage import save
from theme import PRIMARY, GOLD, TEAL, RED, VIOLET, MUTED, EDGE, CARD, CARD2, INK, LV, chip

def spark(parent, sims):
    """Gráfico de linha com a nota geral (0-10) dos últimos simulados."""
    pts, W, H = sims[-12:], 640, 130
    c = ctk.CTkCanvas(parent, width=W, height=H, highlightthickness=0, bg=CARD); c.pack(padx=14, pady=(0, 10))
    for v in (0, 5, 10):
        y = H - 20 - v / 10 * (H - 40)
        c.create_line(30, y, W - 10, y, fill=EDGE); c.create_text(14, y, text=str(v), fill=MUTED, font=("Segoe UI", 8))
    n = len(pts); xs = [30 + (W - 50) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
    ys = [H - 20 - overall(s) / 10 * (H - 40) for s in pts]
    if n > 1: c.create_line(*[v for p in zip(xs, ys) for v in p], fill=VIOLET, width=3, smooth=True)
    for x, y, s in zip(xs, ys, pts):
        c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=GOLD, outline="")
        c.create_text(x, y - 14, text=f"{overall(s):.1f}", fill="white", font=("Segoe UI", 9, "bold"))
        c.create_text(x, H - 6, text=f"{s['date'][8:10]}/{s['date'][5:7]}", fill=MUTED, font=("Segoe UI", 8))

def delete(tab, i):
    sim = tab.app.data["simulados"][i]; n = len(sim.get("attachments", []))
    if messagebox.askyesno("Excluir simulado", f"Excluir “{exam.sim_name(sim)}”" + (f" e seus {n} anexo(s)" if n else "") + "?\nA análise e os reajustes passam a ignorá-lo."):
        if sim.get("id"): exam.remove_attachments(sim["id"])
        del tab.app.data["simulados"][i]; save(tab.app.data); tab.refresh()

def attachments(parent, sim):
    """Anexos do simulado: abrir no programa padrão ou baixar (salvar uma cópia onde quiser). Ficam em anexos/ para sempre."""
    for att in sim.get("attachments", []):
        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", padx=12, pady=1); here = exam.attachment_exists(att)
        ctk.CTkLabel(r, text=f"📎 {att['name']}" + ("" if here else "  (arquivo ausente)"), anchor="w", text_color=MUTED if here else RED).pack(side="left")
        if not here: continue
        def save_as(a=att):
            dest = filedialog.asksaveasfilename(title="Baixar anexo", initialfile=a["name"])
            if dest: exam.export_attachment(a, dest)
        ctk.CTkButton(r, text="Baixar", width=64, height=24, fg_color="gray30", command=save_as).pack(side="right", padx=2)
        ctk.CTkButton(r, text="Abrir", width=64, height=24, command=lambda a=att: open_file(exam.attachment_path(a)), **PRIMARY).pack(side="right", padx=2)

def sim_card(parent, tab, i, sim, deletable=True):
    nota = overall(sim); card = ctk.CTkFrame(parent, fg_color=CARD2); card.pack(fill="x", padx=12, pady=5)
    top = ctk.CTkFrame(card, fg_color="transparent"); top.pack(fill="x", padx=12, pady=(10, 2))
    ctk.CTkLabel(top, text="📝 " + exam.sim_name(sim), font=("Segoe UI", 14, "bold")).pack(side="left")
    if deletable: ctk.CTkButton(top, text="🗑", width=30, fg_color="gray30", command=lambda k=i: delete(tab, k)).pack(side="right")
    ctk.CTkLabel(top, text=f" {nota:.1f}/10 ", fg_color=LV[level(nota)], text_color=INK, corner_radius=9, font=("Segoe UI", 12, "bold")).pack(side="right", padx=8)
    meta = f"{date.fromisoformat(sim['date']):%d/%m/%Y}"
    if "hits" in sim: meta += f"  •  {sim['hits']:g} acertos de {sim['scale']:g}" + (f" (máx. {sim['max_q']} questões)" if sim.get("max_q") and sim["max_q"] != sim["scale"] else "")
    if sim.get("annulled"): meta += f"  •  {sim['annulled']} anulada(s)"
    if sim.get("weighted"): meta += "  •  ⚖ com pesos"
    ctk.CTkLabel(card, text=meta, text_color=MUTED, anchor="w").pack(fill="x", padx=12)
    chips = ctk.CTkFrame(card, fg_color="transparent"); chips.pack(fill="x", padx=12, pady=(4, 4))
    for k, v in sub_scores(sim).items():
        det = sim.get("subjects", {}).get(k, {}); extra = f" ({det['hits']:g}/{det['total']:g})" if "hits" in det and "total" in det else ""
        chip(chips, f"{k} {v:.1f}{extra}", LV[level(v)]).pack(side="left", padx=2, pady=1)
    attachments(card, sim); ctk.CTkLabel(card, text="", height=4).pack()

def build(tab):
    d = tab.app.data; sims = d["simulados"]
    row = ctk.CTkFrame(tab.body, fg_color="transparent"); row.pack(fill="x", pady=(0, 4))
    ctk.CTkButton(row, text="➕ Registrar simulado", command=tab.register, **PRIMARY).pack(side="left")
    if not sims:
        ctk.CTkLabel(tab.body, text="Nenhum simulado registrado ainda.\nQuando você registrar, todos ficam guardados aqui (e no Modo Memória, por ano).", text_color=MUTED).pack(pady=40); return
    sc = [overall(s) for s in sims]
    tab.kpis([("📝", len(sims), "simulados guardados", VIOLET, "{:.0f}"), ("📈", sum(sc) / len(sc), "média geral", GOLD, "{:.1f}"),
              ("🏆", max(sc), "melhor nota", TEAL, "{:.1f}"), ("🕑", sc[-1], "última nota", LV[level(sc[-1])], "{:.1f}")])
    s = tab.section("Evolução das notas (0 a 10)"); spark(s, sims)
    s = tab.section(f"Histórico completo ({len(sims)})")
    if not hasattr(tab, "hq"): tab.hq, tab.hp = "", 1
    ctrl = ctk.CTkFrame(s, fg_color="transparent"); ctrl.pack(fill="x", padx=12, pady=(0, 4))
    ent = ctk.CTkEntry(ctrl, width=380, placeholder_text="🔎 Buscar simulado por nome…"); ent.pack(side="left")
    if tab.hq: ent.insert(0, tab.hq)
    info = ctk.CTkLabel(ctrl, text="", text_color=MUTED); info.pack(side="left", padx=12)
    pager = ctk.CTkFrame(s, fg_color="transparent"); pager.pack(fill="x", padx=12)
    lst = ctk.CTkFrame(s, fg_color="transparent"); lst.pack(fill="x")

    def go(p): tab.hp = p; render()
    def render():
        for w in pager.winfo_children() + lst.winfo_children(): w.destroy()
        items = exam.filter_sims(sims, tab.hq); page, pages, tab.hp = exam.paginate(items, tab.hp)
        info.configure(text=f"{len(items)} simulado(s) • página {tab.hp} de {pages} • até {exam.PER_PAGE} por aba")
        if pages > 1:
            ctk.CTkButton(pager, text="◀", width=34, fg_color="gray30", command=lambda: go(max(1, tab.hp - 1))).pack(side="left", padx=2)
            if pages <= 10:
                seg = ctk.CTkSegmentedButton(pager, values=[str(n) for n in range(1, pages + 1)], command=lambda v: go(int(v))); seg.set(str(tab.hp)); seg.pack(side="left", padx=4)
            else:
                om = ctk.CTkOptionMenu(pager, values=[f"Página {n}" for n in range(1, pages + 1)], command=lambda v: go(int(v.split()[1]))); om.set(f"Página {tab.hp}"); om.pack(side="left", padx=4)
            ctk.CTkButton(pager, text="▶", width=34, fg_color="gray30", command=lambda: go(min(pages, tab.hp + 1))).pack(side="left", padx=2)
        if not items: ctk.CTkLabel(lst, text="Nenhum simulado com esse nome.", text_color=MUTED).pack(pady=16)
        for i, sim in page: sim_card(lst, tab, i, sim)

    def on_key(e):
        tab.hq, tab.hp = ent.get(), 1; render()
    ent.bind("<KeyRelease>", on_key); render()
