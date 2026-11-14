"""Simulados: cálculo por matéria (questões anuladas e abatimento), peso da prova, anexos persistentes, busca e paginação.
Funções puras (sem interface) — usadas pelo diálogo de registro, pelo histórico e pelos testes."""
import math, os, shutil, unicodedata, uuid
import clock
from storage import BASE

ATT_DIR = os.path.join(BASE, "anexos")   # anexos vivem FORA do data.json, em anexos/<id do simulado>/ — nunca são apagados na virada do ano
PER_PAGE = 10

def adjust(total, hits, annulled=0, annulled_hit=None):
    """Questão anulada deixa de existir: o teto da matéria cai exatamente em `anuladas` e os acertos marcados nelas são abatidos.
    Ex.: 20 questões, 3 anuladas, 9 acertos (incluindo as 3 anuladas) -> 6 acertos em 17.
    `annulled_hit` = quantas das anuladas o usuário tinha marcado como acerto (padrão: todas, como no exemplo)."""
    ah = annulled if annulled_hit is None else annulled_hit
    eff_total = total - annulled
    return max(0, min(eff_total, hits - ah)), eff_total

def compute_exam(name, max_q, rows, weighted=False, city_year=0, today=None):
    """rows = [{"subject", "total", "hits", "annulled", "annulled_hit", "weight"}]. Retorna o registro do simulado ou levanta ValueError
    com a mensagem para o usuário. A soma das questões das matérias DEVE ser igual ao máximo de questões da prova."""
    name = (name or "").strip()
    if not name: raise ValueError("Informe o nome da prova.")
    if not isinstance(max_q, int) or max_q < 1: raise ValueError("A quantidade máxima de questões deve ser um número inteiro maior que zero.")
    if not rows: raise ValueError("Selecione ao menos uma matéria.")
    soma = sum(r["total"] for r in rows)
    if soma != max_q: raise ValueError(f"A soma das questões das matérias ({soma}) precisa ser igual ao máximo de questões da prova ({max_q}).")
    subs, H, T, A = {}, 0, 0, 0
    for r in rows:
        s, t, h, a = r["subject"], r["total"], r["hits"], r.get("annulled", 0); ah = r.get("annulled_hit")
        ah = a if ah is None else ah; w = float(r.get("weight", 1) or 0) if weighted else 1.0
        if t < 1: raise ValueError(f"{s}: informe a quantidade de questões (mínimo 1).")
        if not 0 <= h <= t: raise ValueError(f"{s}: os acertos (0 a {t}) não podem passar do total de questões.")
        if not 0 <= a <= t: raise ValueError(f"{s}: as anuladas (0 a {t}) não podem passar do total de questões.")
        if not 0 <= ah <= min(a, h): raise ValueError(f"{s}: dentre as anuladas, os acertos marcados (0 a {min(a, h)}) não podem passar das anuladas nem dos acertos.")
        if weighted and w <= 0: raise ValueError(f"{s}: o peso precisa ser maior que zero.")
        eh, et = adjust(t, h, a, ah)
        if et < 1: raise ValueError(f"{s}: todas as questões foram anuladas — remova a matéria do simulado.")
        subs[s] = {"hits": eh, "total": et, "orig_hits": h, "orig_total": t, "annulled": a, "annulled_hit": ah, "score": round(eh / et * 10, 2), "weight": w}
        H, T, A = H + eh, T + et, A + a
    score = (sum(v["weight"] * v["score"] for v in subs.values()) / sum(v["weight"] for v in subs.values())) if weighted else H / T * 10
    return {"id": uuid.uuid4().hex[:10], "name": name, "date": (today or clock.today()).isoformat(), "max_q": max_q, "hits": H, "scale": T, "annulled": A,
            "score10": round(score, 2), "weighted": bool(weighted), "city_year": city_year, "attachments": [], "subjects": subs}

# ---------- anexos ----------
def add_attachments(sim_id, paths):
    """Copia os arquivos para anexos/<id>/ e devolve a lista [{"name", "file", "size"}] para guardar no simulado."""
    folder = os.path.join(ATT_DIR, sim_id); os.makedirs(folder, exist_ok=True); out = []
    for p in paths:
        name = os.path.basename(p); base, ext = os.path.splitext(name); dest, i = os.path.join(folder, name), 1
        while os.path.exists(dest): dest = os.path.join(folder, f"{base} ({i}){ext}"); i += 1
        shutil.copy2(p, dest); out.append({"name": name, "file": f"{sim_id}/{os.path.basename(dest)}", "size": os.path.getsize(dest)})
    return out
def attachment_path(att): return os.path.join(ATT_DIR, *att["file"].split("/"))
def attachment_exists(att): return os.path.isfile(attachment_path(att))
def export_attachment(att, dest): shutil.copy2(attachment_path(att), dest)
def remove_attachments(sim_id): shutil.rmtree(os.path.join(ATT_DIR, sim_id), ignore_errors=True)

# ---------- busca e paginação ----------
def norm(t): return "".join(c for c in unicodedata.normalize("NFKD", str(t).lower()) if not unicodedata.combining(c))
def sim_name(sim):
    return sim.get("name") or "Simulado " + "/".join(reversed(sim["date"].split("-")))
def filter_sims(sims, query=""):
    """[(índice_original, simulado)] do mais novo para o mais antigo, filtrado por nome (sem acento/maiúsculas; todas as palavras)."""
    words = norm(query).split(); items = list(enumerate(sims))[::-1]
    return [(i, s) for i, s in items if all(w in norm(sim_name(s)) for w in words)]
def paginate(items, page, per=PER_PAGE):
    """(itens da página, nº de páginas, página efetiva) — no máximo `per` simulados por página."""
    pages = max(1, math.ceil(len(items) / per)); page = max(1, min(page, pages)); return items[(page - 1) * per: page * per], pages, page
