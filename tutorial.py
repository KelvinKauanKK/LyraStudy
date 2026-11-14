"""Tutorial embutido (botão ❓ Tutorial): explica o app inteiro — cidade, prédios, praças, simulados e o cálculo do cronograma.
Os números vêm do catálogo (city.catalog), então o texto acompanha as regras."""
import customtkinter as ctk
from theme import GOLD, MUTED, PRIMARY
from city import catalog as C

def sections():
    free, n = sum(1 for b in C.BLD if not b["p"]), len(C.BLD)
    return [
("🧭 Visão geral", f"""O Lyra Study junta organização de estudos e gamificação.

ABAS
• PDFs — explorador de pastas com seus materiais.
• Foco e Loja — cronômetro de estudo e a Lyra City (sua metrópole).
• Cronograma — grade semanal calculada para você + lista de tarefas.
• Revisão — flashcards com repetição espaçada.
• Desempenho — metas, nota do mês, simulados e análise.

NO TOPO
• ✦ Lyra Study (clique no logo) — Modo Memória: fotos da cidade, métricas e simulados de cada ano concluído.
• ⭐ pontos e nível (1 nível a cada 5 h de foco). Os pontos são a moeda da loja da cidade.

Todos os tempos aparecem como "2h e 30 min"."""),
("⏱ Foco, pontos e metas", f"""• Escolha a matéria e inicie o foco. Modo Pomodoro (regressivo, com pausas) ou Progressivo (contagem livre) — botão "Configurar timer".
• Cada minuto de foco rende 10 pontos e {C.XP_PER_MIN} XP para o prédio em foco na cidade.
• META DO DIA: definida no Cronograma (horas por dia). Quando você bate a meta, o dia está CONCLUÍDO e a cidade ganha um quadrado novo.
• ESTUDO GERAL (sem matéria específica) conta automaticamente para a Meta do Dia — o total do dia soma todas as matérias e o Estudo Geral.
• Dias seguidos sem bater a meta (a partir do 2º) geram penalidade de pontos (veja em Desempenho)."""),
("🏙 A cidade", f"""A cidade cresce com os dias em que você bate a meta.

• 1 dia concluído = 1 quadrado (rua, iluminação e uma fundação).
• 7 dias fundem-se em 1 Quadrado de SEMANA (3×3). 4 semanas = 1 Quadrado de MÊS (6×6). 12 meses = o Quadrado do ANO: 12 blocões numa grade 4×3.
• Onde cada mês, semana e dia aparece é sorteado (e fica salvo: o mapa não muda ao reabrir).
• Ao fechar o ano, uma foto do mapa e as métricas são guardadas (Modo Memória) e o mapa recomeça limpo.

VISÕES (topo do mapa): Dia, Semana, Mês e Ano. A câmera é fixa: o mapa é enquadrado sozinho.
BOTÕES: 🛒 Loja (compras) e ⚙ Funções (território, modo foco, fluxo automático e quadrado selecionado). Ambos abrem por cima do mapa; ✕ ou Esc fecham.
Clique num quadrado do mapa para selecioná-lo (ele aparece em Funções)."""),
("🏢 Prédios e níveis", f"""• O catálogo tem {n} modelos de prédio; {free} são grátis e os outros são comprados na Loja com pontos.
• Cada modelo evolui por níveis (3 ou 4, conforme o modelo) e o desenho muda a cada nível.
• O XP do estudo vai para o PRÉDIO EM FOCO (Funções → Modo Foco). Subir do nível n para n+1 custa 100×n XP.
• Ao chegar ao nível máximo, o foco passa sozinho ao próximo prédio que ainda evolui; o prédio em foco continua o mesmo entre os dias.
• FLUXO AUTOMÁTICO (Funções): constrói sozinho em cada novo dia o modelo escolhido; com "Prédio do dia aleatório" o modelo é sorteado entre os que você já tem.
• Fundação livre: selecione o quadrado e escolha o prédio (ou 🎲 aleatório)."""),
("🌳 Praças", f"""As metas das praças valem para o MÊS e reiniciam todo mês:
• 1 hora de estudo no mês → libera a Praça dos Bancos.
• 1 dia concluído no mês → libera a Praça da Fonte.
• 7 dias concluídos no mês → libera a Praça Jardim Real.
Cada liberação ergue uma praça num lote sorteado do mapa.

Com {C.PLAZA_MIN_UNLOCKED} ou mais praças liberadas no mês, surge uma praça nova (aleatória) a cada {C.PLAZA_EVERY} dias concluídos. Sem lote livre, a praça espera a próxima semana abrir lotes.
Ao virar o mês, o progresso e o acesso reiniciam, mas as praças já construídas continuam no mapa.
Na Loja → Praças você vê as metas e escolhe o estilo das praças novas."""),
("🚗 Veículos e ruas", """• Há asfalto em toda a grade, com setas de mão única, separando prédios e praças.
• Os carros circulam pelas ruas em um sentido só e não colidem entre si; passam por trás dos prédios.
• São 6 modelos: 2 grátis e 4 premium (Loja → Veículos). Cidades pequenas têm poucos carros; o tráfego cresce com o mapa."""),
("🗓 Cronograma", """O assistente pergunta: matérias, horas por dia, quantas matérias por dia e a dificuldade de cada uma (1 a 5). Então calcula:
1) soma todos os pesos (dificuldades);
2) meta diária × 7 = horas da semana (em minutos);
3) minutos da semana ÷ soma dos pesos = minutos por ponto de peso;
4) minutos por ponto × peso da matéria = minutos semanais daquela matéria.
Depois distribui as matérias nos 7 dias: cada dia recebe o número de matérias que você escolheu e os dias que sobram recebem uma a mais; matérias mais difíceis aparecem em mais dias.
A lista de tarefas (Hoje / Semana) acompanha a grade. 🔄 Reajustar usa os últimos 3 simulados."""),
("📝 Simulados", """Desempenho → Simulados → ➕ Registrar simulado.
1) Dados da prova: NOME (ex.: ITA 2025) e QUANTIDADE MÁXIMA de questões; marque as matérias que caíram (pode digitar matérias novas).
2) Por matéria: questões, acertos, anuladas e, das anuladas, quantas você tinha marcado como acerto. O TOTAL DE ACERTOS da prova é a soma automática dos acertos por matéria. A soma das questões das matérias tem de ser IGUAL ao máximo da prova.

ANULADAS: a questão anulada deixa de existir. O teto da matéria cai exatamente no número de anuladas e os acertos marcados nelas são abatidos.
Exemplo: 20 questões, 3 anuladas, 9 acertos incluindo as 3 anuladas → vale 6 acertos em 17.

PESOS: se a prova tem pesos diferentes por matéria, ligue "A prova possui pesos diferentes" e digite o peso de cada uma. A nota geral vira uma média ponderada e o cronograma passa a priorizar peso × taxa de erro.
ANEXOS: anexe PDFs, fotos de redações, provas rabiscadas. Ficam guardados para sempre na pasta "anexos" (ao lado do app) e podem ser abertos ou baixados a qualquer momento — a virada do ano não apaga nada.
Histórico: busque por nome e navegue pelas abas (10 simulados por aba). No Modo Memória (clique no logo) veja os simulados e anexos de cada ano."""),
("🔄 Reajuste do cronograma", """Depois de registrar um simulado o app sugere novas dificuldades (1 a 5) usando ESTRITAMENTE os últimos 3 simulados:
• nota média de cada matéria (0 a 10) → taxa de erro;
• prioridade = taxa de erro × peso da matéria na prova (sem pesos, só o erro);
• dificuldade = 1 + 4 × prioridade (máx. 5), com ±0,5 se a nota caiu ou subiu bastante.
Matérias que valem mais e onde você mais erra ganham mais minutos na grade. Você vê as mudanças e decide: "Aceita a Nova Grade?".
Sem simulados há mais de 1 mês, um aviso aparece em Desempenho recomendando revisar as dificuldades."""),
("📊 Desempenho e nota do mês", """• Metas de hoje e da semana, matérias pendentes e penalidades do ano.
• NOTA DO MÊS (0 a 10): cumprimento de metas (40%) + constância, que é a fração de dias com pelo menos metade da meta (30%) + resultados dos 3 últimos simulados (30%). Sem simulados, o peso se divide entre metas e constância.
• Visão Mês: progresso acumulado, ritmo, calendário colorido e tempo por matéria. Visão Simulados: evolução, busca e histórico."""),
("📚 PDFs e 🧠 Revisão", """PDFs: abra pastas e subpastas, volte pela trilha, crie/remova pastas (removidas vão para _Removidas), mova PDFs entre pastas e marque "Estudado".
Revisão: crie cartões (texto e imagens), organize por matéria › categoria › subcategoria e estude: Errei / Difícil / Bom / Fácil reagendam a próxima revisão."""),
("💾 Seus dados", """Tudo fica ao lado do programa:
• data.json — progresso, cidade, simulados e histórico anual.
• anexos/ — arquivos anexados aos simulados.
• snapshots/ — fotos PNG exportadas do Modo Memória.
• PDFs/ e Imagens/ — seus materiais e imagens dos flashcards.
Para fazer backup ou trocar de computador, copie essa pasta inteira."""),
]

class TutorialDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master); self.title("Tutorial — Lyra Study"); self.geometry("980x640"); self.transient(master.winfo_toplevel())
        ctk.CTkLabel(self, text="❓ Como o Lyra Study funciona", font=("Segoe UI", 20, "bold"), text_color=GOLD).pack(pady=(14, 6))
        body = ctk.CTkFrame(self, fg_color="transparent"); body.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        side = ctk.CTkScrollableFrame(body, width=230); side.pack(side="left", fill="y", padx=(0, 10))
        self.box = ctk.CTkTextbox(body, wrap="word", font=("Segoe UI", 14)); self.box.pack(side="left", fill="both", expand=True)
        self.secs = sections(); self.btns = []
        for i, (t, _) in enumerate(self.secs):
            b = ctk.CTkButton(side, text=t, anchor="w", fg_color="transparent", hover_color="gray25", command=lambda i=i: self.show(i)); b.pack(fill="x", pady=2); self.btns.append(b)
        self.show(0)

    def show(self, i):
        for k, b in enumerate(self.btns): b.configure(fg_color=GOLD if k == i else "transparent", text_color="#14161f" if k == i else "#e8eaf6")
        t, text = self.secs[i]; self.box.configure(state="normal"); self.box.delete("1.0", "end"); self.box.insert("1.0", t + "\n\n" + text); self.box.configure(state="disabled")
