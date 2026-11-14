"""Base dos painéis em OVERLAY da cidade (Loja e Funções): mesmo visual e mesmo comportamento de sobreposição — cobrem o mapa
(place), fecham com ✕ ou Esc, e só um fica aberto por vez."""
import customtkinter as ctk
from theme import GOLD

class Overlay(ctk.CTkFrame):
    title = ""

    def __init__(self, master, w):
        super().__init__(master, corner_radius=16, border_width=2, border_color=GOLD)
        self.w, self.opened = w, False
        head = ctk.CTkFrame(self, fg_color="transparent"); head.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(head, text=self.title, font=("Segoe UI", 18, "bold"), text_color=GOLD).pack(side="left")
        self.head_extra = ctk.CTkFrame(head, fg_color="transparent"); self.head_extra.pack(side="left", padx=14)
        ctk.CTkButton(head, text="✕ Fechar", width=84, fg_color="gray30", command=self.close).pack(side="right")
        self.content = ctk.CTkFrame(self, fg_color="transparent"); self.content.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    def toggle(self): self.close() if self.opened else self.open()
    def open(self):
        self.w.close_overlays(self); self.opened = True; self.place(relx=.015, rely=.02, relwidth=.97, relheight=.96); self.lift()
        self.winfo_toplevel().bind("<Escape>", lambda e: self.close()); self.refresh()
    def close(self):
        self.opened = False; self.place_forget()
        try: self.winfo_toplevel().unbind("<Escape>")
        except Exception: pass
    def refresh(self): pass          # cada overlay redesenha seu conteúdo (só quando aberto)
