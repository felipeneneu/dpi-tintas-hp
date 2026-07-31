# DPI Tintas HP

**Controle de Consumo de Tintas CMYK para Impressao**

Aplicativo desktop leve e moderno para registrar o consumo de tintas CMYK por rodagem de impressao e calcular o custo financeiro exato com base no historico armazenado em SQLite.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-6.0-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Funcionalidades

- **Controle CMYK** - Cards para cada cor com campos % Inicial e % Final
- **Calculo Automatico** - Custo por cor e total em R$ (centavos)
- **Historico de Rodagens** - Todas as rodagens registradas no SQLite
- **Reabastecimento** - Botao 100% para resetar nivel do cartucho
- **Configuracao** - Ajustar capacidade (ml) e preco (R$) de cada cartucho
- **Exportacao** - Backup em JSON ou script SQL
- **Dark/Light Mode** - Tema claro e escuro

---

## Arquitetura MVC

```
┌─────────────────────────────────────────────────────────┐
│                    MAIN VIEW                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Menu Bar (Arquivo | Editar | Exibir)           │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Header (Logo + Titulo)                         │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Cards CMYK (C | M | Y | K)                     │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐           │   │
│  │  │  C  │  │  M  │  │  Y  │  │  K  │           │   │
│  │  └─────┘  └─────┘  └─────┘  └─────┘           │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  [CALCULAR & REGISTRAR RODAGEM]                 │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  ResultCard (Custo Total: R$ XX,XX)             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   CONTROLLER                            │
│  - Conecta View <-> Model                               │
│  - Processa acoes do usuario                            │
│  - Valida dados                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                     MODEL                               │
│  - Database SQLite (tintas_controle.db)                 │
│  - TintaModel (regra de negocio)                        │
│  - Calculo de custos                                    │
│  - Exportacao JSON/SQL                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Estrutura de Pastas

```
dpi-tintas-hp/
├── config/
│   ├── __init__.py
│   └── theme.py              # Design System (Cores, Fontes, Paths)
├── models/
│   ├── __init__.py
│   ├── database.py           # Conexao SQLite e tabelas
│   └── tinta_model.py        # Regra de negocio CMYK
├── views/
│   ├── __init__.py
│   ├── components.py         # CmykCard, PercentEntry, ResultCard
│   ├── main_view.py          # Interface principal
│   └── config_modal.py       # Modal de configuracao
├── controllers/
│   ├── __init__.py
│   └── main_controller.py    # Conecta View <-> Model
├── src/images/
│   ├── logo.png              # Logo DPI Visual
│   └── favicon.ico           # Icone da janela
├── main.py                   # Ponto de entrada
├── build.py                  # Script de compilacao
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
git clone https://github.com/dpivisual/dpi-tintas-hp.git
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

Para gerar um executavel standalone:

```bash
python build.py
```

O executavel sera gerado em `dist/DPI-Tintas-HP.exe`.

---

## Uso

### Registrar Rodagem

1. Preencha o campo **% Inicial** (preenchido automaticamente com ultimo nivel)
2. Preencha o campo **% Apos uso** (nivel apos a rodagem)
3. Clique em **CALCULAR & REGISTRAR RODAGEM**
4. O custo total sera exibido no card verde

### Reabastecer Cartucho

1. Clique no botao **100%** ao lado do cartucho
2. O nivel sera resetado para 100%

### Configurar Cartuchos

1. Va em **Editar > Configurar Cartuchos**
2. Ajuste a capacidade (ml) e preco (R$) de cada cartucho
3. Clique em **Salvar**

### Exportar Dados

1. Va em **Arquivo > Exportar JSON** ou **Exportar SQL**
2. Escolha onde salvar o arquivo

### Alternar Tema

1. Va em **Exibir > Alternar Light/Dark**

---

## Estrutura do Banco de Dados

### Tabela: configuracao

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| cor | TEXT (PK) | C, M, Y ou K |
| capacidade_ml | REAL | Capacidade do cartucho em ml |
| preco_cartucho_centavos | INTEGER | Preco em centavos |
| nivel_atual_pct | REAL | Nivel atual (0-100%) |

### Tabela: rodagens

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | INTEGER (PK) | Identificador unico |
| data_hora | TIMESTAMP | Data e hora da rodagem |
| c_ini, m_ini, y_ini, k_ini | REAL | Niveis iniciais (%) |
| c_fim, m_fim, y_fim, k_fim | REAL | Niveis finais (%) |
| custo_total_centavos | INTEGER | Custo total em centavos |

---

## Formulas de Calculo

```
Gasto (%) = Nivel Inicial - Nivel Final
Custo (centavos) = (Gasto / 100) * Preco Cartucho (centavos)
Custo Total = Soma dos custos de C + M + Y + K
```

---

## Tecnologias

- **Python 3.13** - Linguagem principal
- **CustomTkinter 6.0** - Interface grafica moderna
- **SQLite3** - Banco de dados local
- **Pillow** - Manipulacao de imagens
- **PyInstaller** - Geracao de executavel

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
| Success | #10B981 | Resultado/custo |
| Danger | #EF4444 | Botoes de reabastecer |

### Tipografia

| Fonte | Uso |
|-------|-----|
| Segoe UI 18px Bold | Titulos |
| Segoe UI 14px Bold | Subtitulos |
| Segoe UI 12px Bold | Labels |
| Consolas 14px Bold | Valores |

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
