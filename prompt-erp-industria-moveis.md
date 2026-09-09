# PROMPT MESTRE — Desenvolvimento de Sistema ERP para Indústria de Móveis (PCP, Custos e Precificação)

## 1. Papel e Objetivo

Você é uma equipe de engenharia de software full-stack (arquiteto de banco de dados, back-end, front-end e QA) responsável por projetar e construir, do zero, uma **plataforma web personalizada de gestão industrial (ERP)** para uma empresa de pequeno porte fabricante de cadeiras e banquetas para mesas de jantar.

A empresa opera em regime de **fabricação seriada** e tributa pelo **Lucro Real (Anexo II)**. O objetivo do sistema é dar controle total sobre o fluxo produtivo, a apropriação de custos industriais, o rastreamento de insumos e a formação de preços de venda.

> **Observação para validação com o cliente antes de iniciar:** o briefing original cita simultaneamente "Lucro Real (Anexo II)" e, na Etapa 3, "Parametrização Fiscal (Simples Nacional)". O Anexo II é uma tabela do Simples Nacional, não do Lucro Real — são regimes tributários distintos com lógicas de apuração diferentes. Antes de iniciar o desenvolvimento do módulo fiscal, confirme com o cliente qual é o regime tributário real da empresa, pois isso muda inteiramente o motor de cálculo de impostos e de formação de preço.

Entregue uma solução ponta a ponta: banco de dados estruturado, back-end, front-end responsivo e relatórios exportáveis.

## 2. Stack Tecnológica Sugerida

Adapte conforme restrições do cliente, mas na ausência de uma stack imposta, utilize:

- **Front-end:** Next.js (React + TypeScript), com componentização modular por domínio (produção, estoque, custos, fiscal, BI)
- **Back-end:** API REST ou GraphQL em Node.js/TypeScript (NestJS) **ou** Laravel (PHP), conforme preferência do time
- **Banco de dados:** PostgreSQL (recomendado por integridade referencial forte, essencial para BOM multinível e rastreabilidade de custos)
- **ORM:** Prisma (Node) ou Eloquent (Laravel)
- **Autenticação:** JWT com controle de perfis (admin, PCP, almoxarifado, financeiro, diretoria)
- **Exportação de relatórios:** biblioteca de geração de PDF (ex.: Puppeteer/DomPDF) e Excel (ex.: SheetJS/PhpSpreadsheet)
- **Dashboard:** biblioteca de gráficos (Recharts, Chart.js ou ApexCharts)
- **Infraestrutura:** Docker para ambiente de desenvolvimento e homologação

## 3. Modelagem de Dados — Entidades Centrais

Antes de codificar, projete um modelo de dados que suporte, no mínimo, estas entidades e seus relacionamentos:

- `Produto` (cadeira/banqueta — modelo final vendável)
- `ComponenteBOM` (estrutura multinível de insumos por produto — Bill of Materials)
- `Insumo` (matéria-prima: madeira, tecido, espuma, ferragem, químico de acabamento)
- `PostoDeTrabalho` (corte, usinagem, montagem, acabamento/lixamento, pintura/envernizamento, estofamento)
- `TempoPadrao` (cronoanálise por posto de trabalho, usada para apropriar MOD)
- `OrdemDeProducao` (OP) com `EtapaOP` (uma por fase produtiva) e `ApontamentoOP` (registros de perdas, refugos, retrabalhos)
- `MovimentacaoEstoque` (entradas, saídas, transferências internas) vinculada a `Insumo` e `ProdutoAcabado`
- `ParametroEstoque` (estoque mínimo, ponto de pedido, estoque de segurança) por insumo
- `RateioCIF` (regras de rateio de custos indiretos de fabricação, fixos e variáveis)
- `RegimeTributario` / `AliquotaFiscal` (parametrização dinâmica das alíquotas aplicáveis)
- `SimulacaoPreco` (markup divisor/multiplicador, tributos, comissões, despesas operacionais, margem líquida)
- `Usuario` / `Perfil` (controle de acesso)

Todo relacionamento entre OP, insumo e estoque deve ser rastreável (auditoria de baixa por explosão de insumos).

## 4. Módulos Funcionais

Desenvolva os 6 módulos abaixo de forma integrada — nenhum deles deve ser tratado como sistema isolado; todos compartilham o mesmo modelo de dados central.

### Módulo 1 — Controle de Fabricação e Produção (PCP)
- Emissão, acompanhamento e encerramento de Ordens de Produção (OPs)
- Mapeamento das 6 etapas produtivas: corte → usinagem → montagem → acabamento/lixamento → pintura/envernizamento → estofamento
- Registro e apontamento de perdas, refugos e retrabalhos por fase, com motivo e responsável
- **Critério de aceite:** emissão de OPs com baixa e movimentação entre etapas sem inconsistências (nenhuma etapa pode avançar sem que a anterior esteja concluída ou formalmente pulada com justificativa).

### Módulo 2 — Capacidade Produtiva e Análise de Gargalos
- Cálculo automático de capacidade nominal e efetiva por posto de trabalho e consolidada (peças/dia, peças/semana, peças/mês)
- Identificação gráfica e analítica do processo gargalo da planta
- Balanceamento de linha e planejamento de capacidade frente aos pedidos em carteira
- **Critério de aceite:** demonstração em tempo real da linha gargalo conforme os parâmetros informados (tempos-padrão, turnos, absenteísmo/paradas).

### Módulo 3 — Ficha Técnica e Apuração de Custos (Custo de Fabricação)
- Estrutura multinível de produtos (BOM) por modelo de cadeira/banqueta
- Custeio direto de matérias-primas (madeira, tecidos, espumas, ferragens, químicos)
- Apropriação de mão de obra direta (MOD) com base em tempos-padrão de cronoanálise por posto
- Rateio de custos indiretos de fabricação (CIF fixos e variáveis)
- Apuração automatizada do Custo Unitário de Fabricação (CUF)
- **Critério de aceite:** cálculo do custo total de fabricação batendo com a planilha base do cliente (peça de referência para validação).

### Módulo 4 — Controle de Estoque e Almoxarifado
- Gestão de inventário em tempo real (entradas, saídas, movimentações internas) de insumos e produtos acabados
- Parâmetros de estoque mínimo, ponto de pedido e estoque de segurança
- Alertas visuais automáticos de necessidade de reposição
- Baixa automática por explosão de insumos ao concluir cada OP
- **Critério de aceite:** disparo de alerta ao atingir o ponto de reposição e baixa automática correta pós-OP.

### Módulo 5 — Tributação e Formação de Preço de Venda
- Parametrização dinâmica de alíquotas do regime tributário aplicável (**confirmar com o cliente** — ver observação na seção 1)
- Motor de cálculo de formação de preço via markup divisor e multiplicador sobre o custo fabril
- Simulação de preço de venda sugerido, deduzindo tributos, comissões de venda, despesas operacionais e margem de lucro líquido pretendida
- **Critério de aceite:** simulação correta de preço sugerido e apuração exata do imposto devido, validada contra cálculo manual do cliente.

### Módulo 6 — Painel Gerencial e Relatórios (Business Intelligence)
- Dashboard executivo responsivo com KPIs: volume produzido, taxa de ocupação fabril, custo médio ponderado, margem de contribuição por linha
- Relatórios analíticos e sintéticos com exportação nativa em PDF e Excel (.xlsx)
- **Critério de aceite:** geração de relatórios operacionais e financeiros em conformidade com os dados do banco.

## 5. Etapas de Entrega (Valor Fixo, com homologação por etapa)

1. **Etapa 1:** Modelagem do banco de dados, arquitetura web, módulo de Cadastros/Ficha Técnica (BOM)
2. **Etapa 2:** Módulo de Estoque + Módulo de Ordens de Produção (Fabricação, Capacidade e Apontamentos)
3. **Etapa 3:** Módulo de Custos Industriais, Parametrização Fiscal e Simulador de Preço de Venda
4. **Etapa 4:** Dashboard Executivo, Relatórios Gerenciais, Testes Integrados, Correção de Bugs, Homologação Final

Cada etapa deve ser entregue com dados de teste realistas e roteiro de homologação (checklist de aceite) para validação do cliente antes de avançar para a próxima.

## 6. Requisitos Não Funcionais

- Interface responsiva (uso em desktop no chão de fábrica/escritório e tablet no almoxarifado)
- Controle de acesso por perfil (operador de produção não deve ver dados financeiros/fiscais)
- Auditoria/log de alterações em OPs, estoque e parâmetros fiscais
- Performance: cálculos de custo e capacidade devem responder em tempo real ao alterar parâmetros
- Testes automatizados para as regras de cálculo (custeio, rateio, formação de preço) — são a parte mais sensível a erro silencioso

## 7. Instrução Final para o Agente

Ao gerar o código, priorize nesta ordem:
1. Modelo de dados correto e migrations
2. Regras de negócio de custeio e PCP (o coração do sistema)
3. APIs
4. Front-end
5. Dashboard/relatórios por último, pois dependem dos dados já consistentes

Sempre que uma regra de negócio (rateio de CIF, cálculo de imposto, cronoanálise) não estiver 100% especificada, pare e liste as perguntas de esclarecimento em vez de assumir uma fórmula — erros de custeio nesse tipo de sistema se propagam para o preço de venda final.
