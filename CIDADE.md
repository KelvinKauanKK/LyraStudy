# Lyra City dentro do Lyra Study

A cidade vive na aba **Foco e Loja** (`focus.py` → `city.widget.CityWidget`). Python + CustomTkinter + Pillow (entra no mesmo `.exe` do PyInstaller).

```
city/
  catalog.py   prédios (lidos de assets/city/buildings.json), carros, praças, constantes (STREET, BLD_FILL, ROAD_W, TRAFFIC, intervalos do laço)
  layout.py    posições ALEATÓRIAS e reprodutíveis: mês -> 1 dos 12 blocões, semana -> 1 de 4 quadrantes, dia -> 1 de 9 células
  engine.py    regras: XP/níveis, dias, fusões, praças (ciclo mensal), histórico anual (Modo Memória), migração de saves
  traffic.py   carros em ruas de mão única (sem colisão entre si, -20% de tráfego)
  render.py    Pillow: malha viária, profundidade única (carros escondem atrás de prédios), câmera fixa, animações, cache
  widget.py    canvas + laço seguro (um único after) + botão 🛒 Loja   |  panel.py  foco/fluxo automático/prédio do dia aleatório
  shop.py      LOJA em overlay (minimapa + Prédios/Veículos/Praças)    |  functions.py  FUNÇÕES em overlay (território, modo foco, fluxo automático, quadrado selecionado)
  memory.py    Modo Memória (clique no logo): foto do ano, métricas, simulados e anexos do ano
admin.py       modo Admin só por Ctrl+Shift+A (senha fixa, guardada como hash), simulação de estudo e de calendário   |  clock.py  relógio virtual   |  util.py  fmt_dur
exam.py        simulados: anuladas, abatimento, pesos, anexos persistentes, busca e paginação   |  history.py  aba Simulados   |  tutorial.py  tutorial embutido
library.py     explorador de PDFs (pastas aninhadas)
assets/city/   sprites WebP + meta.json + buildings.json (gerados por tools/process_assets.py)   |  art-source/  artes originais
docs/NOVOS_PREDIOS.md   como inserir novos modelos de prédio e prompts
```

## Regras principais
- **Dia concluído** = meta diária do Lyra Study batida. **XP**: 4 por minuto de foco no prédio em foco (nível n→n+1 custa 100·n XP).
- **Praças (metas do MÊS, reiniciam todo mês):** 1 h de estudo → Praça dos Bancos • 1 dia → Praça da Fonte • 7 dias → Praça Jardim Real. Cada liberação
  ergue uma praça num lote de sobra sorteado (2 lotes de sobra por semana). Com 2+ praças liberadas no mês, surge uma praça nova ao acaso a cada 5 dias
  (sem lote livre, fica na fila). As praças já construídas continuam no mapa; só o progresso/acesso reinicia.
- **Ruas:** asfalto em toda a grade (rua de 0,40 célula) com setas de mão única; carros trafegam no eixo, sem colisão. Praças e prédios ficam em lotes separados pelas ruas.
- **Ano:** 12 blocões em grade compacta 4×3 (24×18), sem buraco no meio. Ao fechar o ano, o estado é guardado em `data["city"]["history"]` e o mapa recomeça.
- **Modo Memória:** clique no logo ✦ Lyra Study → escolha o ano → "foto" renderizada do estado guardado + métricas (dias, tempo "2h e 30 min", prédios, níveis, praças, carros); botão salva PNG em `snapshots/`.
- **Admin:** botão 🔐 Admin (ou Ctrl+Shift+A). Primeiro acesso: você cria a senha (guardada só como hash). Logado: adiantar estudo (pontos+XP+níveis na hora), +pontos, +níveis,
  avançar calendário (+1 dia, +7, +1 mês, +1 ano — a data do app inteiro muda; os dias contam como meta cumprida, sem pontos). Esqueceu a senha: apague a chave "admin" do `data.json`.

## Segurança do laço e cache (ver também a revisão anterior)
Um único `after()` (33 ms; 50 ms se pesado; 100 ms com a aba oculta), `winfo_exists()` antes de cada quadro, exceções no desenho não derrubam o laço,
câmera fixa, sprites e tamanhos em cache (0 `Image.open` e 0 `resize` por quadro).

## Simulados (resumo das regras)
- **Registro:** nome da prova + quantidade máxima de questões + matérias. Por matéria: questões, acertos, anuladas e, das anuladas, quantas estavam marcadas como acerto
  (padrão: todas — como no exemplo). O total de acertos da prova é a soma automática; a soma das questões das matérias tem de ser igual ao máximo (`exam.compute_exam`).
- **Anuladas:** `exam.adjust(total, acertos, anuladas, anuladas_acertadas)` → 20 questões, 3 anuladas, 9 acertos (incluindo as 3) = **6 de 17**.
- **Pesos:** com "A prova possui pesos diferentes por matéria?" = Sim, a nota geral é média ponderada e o ajuste do cronograma usa **prioridade = taxa de erro × peso relativo**
  (`rules.analyze` / `propose_adjustment`, sempre com os últimos 3 simulados). Sem pesos, é o cálculo padrão.
- **Anexos:** copiados para `anexos/<id do simulado>/` (fora do data.json; nunca apagados na virada do ano ou ao reiniciar a cidade). Abrir/Baixar no histórico e no Modo Memória.
- **Histórico:** busca por nome (sem acento/maiúsculas) e abas com no máximo 10 simulados. Cada simulado guarda `city_year`, então o Modo Memória mostra os simulados e anexos de cada ano.
