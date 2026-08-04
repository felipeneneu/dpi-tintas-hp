# DPI Tintas HP

**Controle de Consumo de Tintas para HP Latex 330**

Aplicativo desktop para registrar o consumo de tintas por ciclo de impressao, gerenciar pedidos e bobinas, e calcular o custo financeiro com base no historico armazenado em SQLite.

![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-purple)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)

---

## Funcionalidades

- **7 Cores de Tinta** - C, M, Y, K, LC (Light Cyan), LM (Light Magenta), OP (Opaca)
- **Controle em ml** - Campos Inicial/Final em mililitros (capacidade padrao 775ml)
- **Pedidos (OS)** - Gerenciar pedidos com numero e nome
- **Bobinas** - Gerenciar bobinas com tamanho, material e tipo
- **Ciclo de Impressao** - Timer com Iniciar/Finalizar para medir duracao
- **Campo Arquivo** - Registrar nome do arquivo impresso
- **Calculo Automatico** - Custo por cor e total em R$
- **Busca Inteligente** - Filtros por data, pedido e nome de arquivo
- **Relatorios** - Diario/Semanal com exportacao PDF e Excel
- **Reabastecimento** - Botao 775ml para resetar nivel do cartucho
- **Configuracao** - Ajustar preco de cada cartucho
- **Exportacao** - Backup em JSON ou script SQL
- **Dark/Light Mode** - Tema claro e escuro
- **Migracao Automatica** - Dados v1 (%, 100ml) migrados para v2 (ml, 775ml)

---

## Arquitetura MVC

```
┌──────────────────────────────────────────────────────────────┐
│                       MAIN VIEW                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Menu Bar (Arquivo | Editar | Exibir | Buscar | Rel.) │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Header (Logo DPI + Titulo + Badges 7 cores)          │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Pedido (Numero | Nome | Gerenciar)                    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Bobina (Combo | Tamanho | Material | Tipo | Gerenc.) │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Ciclo (Arquivo | Iniciar | Finalizar | Timer)         │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Niveis de Tinta (3 por linha)                         │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐                          │  │
│  │  │  C   │ │  M   │ │  Y   │                          │  │
│  │  └──────┘ └──────┘ └──────┘                          │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐                          │  │
│  │  │  K   │ │  LC  │ │  LM  │                          │  │
│  │  └──────┘ └──────┘ └──────┘                          │  │
│  │  ┌──────┐                                             │  │
│  │  │  OP  │                                             │  │
│  │  └──────┘                                             │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  [CALCULAR & REGISTRAR]                                │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  ResultCard (Custo Total: R$ XX,XX)                    │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Relatorios (Diario | Semanal | PDF | Excel)           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      CONTROLLER                              │
│  - Conecta View <-> Model                                    │
│  - Processa acoes do usuario                                 │
│  - Valida e converte dados                                    │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                        MODEL                                 │
│  - Database SQLite (tintas_controle.db)                      │
│  - TintaModel (regra de negocio)                             │
│  - PedidoModel / BobinaModel (CRUD)                          │
│  - Calculo de custos em ml                                   │
│  - Historico e busca                                         │
│  - Exportacao JSON/SQL                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Pastas

```
dpi-tintas-hp/
├── config/
│   ├── __init__.py
│   └── theme.py              # Design System (Cores, Fontes, Espacamento)
├── models/
│   ├── __init__.py
│   ├── database.py           # Conexao SQLite, tabelas, migracao v1->v2
│   ├── tinta_model.py        # Regra de negocio (7 cores, ml, custos)
│   ├── pedido_model.py       # CRUD de pedidos
│   └── bobina_model.py       # CRUD de bobinas
├── views/
│   ├── __init__.py
│   ├── components.py         # ColorCard, MlEntry, PrimaryButton, ResultCard
│   ├── main_view.py          # Interface principal
│   ├── config_modal.py       # Modal de configuracao (7 cores)
│   ├── pedido_modal.py       # Modal de gerenciamento de pedidos
│   ├── bobina_modal.py       # Modal de gerenciamento de bobinas
│   ├── historico_view.py     # Historico com busca e filtros
│   └── relatorio_view.py     # Relatorios diario/semanal
├── controllers/
│   ├── __init__.py
│   └── main_controller.py    # Conecta View <-> Model
├── scripts/
│   └── create_db.py          # Criacao do banco de dados
├── src/images/
│   ├── logo.png              # Logo DPI Visual
│   └── favicon.ico           # Icone da janela
├── tests/
│   ├── test_database.py      # Testes do banco e migracao
│   ├── test_tinta_model.py   # Testes da regra de negocio
│   ├── test_controller.py    # Testes do controller
│   └── test_theme.py         # Testes do design system
├── main.py                   # Ponto de entrada
├── build.py                  # Script de compilacao (PyInstaller + Inno Setup)
├── installer.iss             # Script Inno Setup v2.0.0
├── requirements.txt          # Dependencias
├── LICENSE                   # Licenca MIT
└── README.md                 # Esta documentacao
```

---

## Pre-requisitos

- Python 3.13 ou superior
- pip (gerenciador de pacotes)

---

## Instalacao

### 1. Clonar o repositorio

```bash
git clone https://github.com/felipeneneu/dpi-tintas-hp.git
cd dpi-tintas-hp
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Executar o aplicativo

```bash
python main.py
```

---

## Empacotamento (.exe)

Para gerar o executavel e instalador:

```bash
python build.py
```

- Executavel: `dist/DPI-Tintas-HP.exe`
- Instalador: `installer/DPI-Tintas-HP-Setup.exe`

---

## Uso

### Registrar Impressao

1. Selecione o **Pedido** (ou crie um novo em Gerenciar)
2. Selecione a **Bobina** ativa
3. Digite o **nome do arquivo** impresso
4. Clique em **Iniciar** (inicia o timer)
5. Preencha os niveis **Inicial** e **Final** de cada cor (em ml)
6. Clique em **Finalizar** (para o timer)
7. Clique em **CALCULAR & REGISTRAR**

### Gerenciar Pedidos

1. Clique em **Gerenciar** na secao Pedido
2. Adicione, edite ou remova pedidos

### Gerenciar Bobinas

1. Clique em **Gerenciar** na secao Bobina
2. Adicione bobinas com tamanho, material e tipo

### Reabastecer Cartucho

1. Clique no botao **775** ao lado do cartucho
2. O nivel sera resetado para 775ml

### Configurar Precos

1. Va em **Editar > Configurar Cartuchos**
2. Ajuste o preco (R$) de cada cor
3. Clique em **Salvar**

### Buscar Historico

1. Va em **Buscar > Buscar Historico** ou clique em Buscar
2. Use filtros por data, pedido ou nome de arquivo

### Gerar Relatorios

1. Va em **Relatorios > Relatorio Diario/Semanal**
2. Ou use os botoes na secao Relatorios
3. Exporte como PDF ou Excel

### Exportar Dados

1. Va em **Arquivo > Exportar JSON** ou **Exportar SQL**

### Alternar Tema

1. Va em **Exibir > Alternar Light/Dark**

---

## Estrutura do Banco de Dados

### Tabela: configuracao

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| cor | TEXT (PK) | C, M, Y, K, LC, LM ou OP |
| capacidade_ml | REAL | Capacidade do cartucho (padrao 775ml) |
| preco_cartucho_centavos | INTEGER | Preco em centavos |
| nivel_atual_ml | REAL | Nivel atual em ml |

### Tabela: rodagens

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | INTEGER (PK) | Identificador unico |
| data_hora | TIMESTAMP | Data e hora do registro |
| pedido_id | INTEGER (FK) | Referencia ao pedido |
| bobina_id | INTEGER (FK) | Referencia a bobina |
| nome_arquivo | TEXT | Nome do arquivo impresso |
| c_ini, m_ini, y_ini, k_ini, lc_ini, lm_ini, op_ini | REAL | Niveis iniciais (ml) |
| c_fim, m_fim, y_fim, k_fim, lc_fim, lm_fim, op_fim | REAL | Niveis finais (ml) |
| custo_total_centavos | INTEGER | Custo total em centavos |
| duracao_segundos | INTEGER | Duracao do ciclo em segundos |

### Tabela: pedidos

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | INTEGER (PK) | Identificador unico |
| numero | TEXT | Numero do pedido/OS |
| nome | TEXT | Nome/descricao do pedido |

### Tabela: bobinas

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | INTEGER (PK) | Identificador unico |
| nome | TEXT | Nome da bobina |
| tamanho | TEXT | Tamanho (ex: 1m, 2m) |
| material | TEXT | Material (ex: PVC, Lona) |
| tipo | TEXT | Tipo (ex: Front Light, Back Light) |

---

## Formulas de Calculo

```
Gasto (ml) = Nivel Inicial (ml) - Nivel Final (ml)
Custo (centavos) = (Gasto / Capacidade) * Preco Cartucho (centavos)
Custo Total = Soma dos custos de C + M + Y + K + LC + LM + OP
```

---

## Tecnologias

- **Python 3.13+** - Linguagem principal
- **CustomTkinter** - Interface grafica moderna (estilo macOS)
- **SQLite3** - Banco de dados local
- **Pillow** - Manipulacao de imagens
- **openpyxl** - Geracao de planilhas Excel
- **fpdf2** - Geracao de relatorios PDF
- **PyInstaller** - Geracao de executavel
- **Inno Setup** - Gerador de instalador Windows
- **pytest** - Suite de testes (84 testes)

---

## Design System

### Cores

| Nome | Hex | Uso |
|------|-----|-----|
| Primary (Ciano DPI) | #00AEEF | Botoes principais, destaques |
| Cyan | #00AEEF | Cartucho C |
| Magenta | #EC008C | Cartucho M |
| Yellow | #EAB308 | Cartucho Y |
| Black | #334155 | Cartucho K |
| Light Cyan | #67C7E0 | Cartucho LC |
| Light Magenta | #F49AC2 | Cartucho LM |
| Opaca | #8B8B8B | Cartucho OP |
| Success | #10B981 | Resultado/custo, Iniciar |
| Danger | #EF4444 | Reabastecer, PDF |
| Warning | #F59E0B | Finalizar |

### Tipografia

| Fonte | Uso |
|-------|-----|
| Segoe UI 18px Bold | Titulos |
| Segoe UI 14px Bold | Subtitulos |
| Segoe UI 12px Bold | Labels, Botoes |
| Segoe UI 12px | Corpo de texto |
| Cascadia Code 13px Bold | Valores numericos |

---

## Testes

```bash
python -m pytest tests/ -v
```

84 testes cobrindo: database, migracao, tinta_model, controller e theme.

---

## CI/CD

O GitHub Actions executa automaticamente:

- **CI**: Validacao de compilacao e imports (toda push/PR)
- **CD**: Build do .exe + instalador + release (tag `v*`)

---

## Licenca

Este projeto esta licenciado sob a licenca MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Contato

**DPI Visual**
- Site: [dpivisual.com.br](https://dpivisual.com.br)
- Email: contato@dpivisual.com.br

---

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas alteracoes (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request
