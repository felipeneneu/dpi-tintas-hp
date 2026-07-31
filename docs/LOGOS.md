# Logos DPI Tintas HP - Especificacoes

## Estrutura de Pastas

```
src/images/
├── logo-16x16.png         # Icone da janela (title bar)
├── logo-32x32.png         # Taskbar Windows
├── logo-48x48.png         # Dialog "Sobre" / Header
├── logo-64x64.png         # Splash screen
├── logo-128x128.png       # About dialog
├── logo-256x256.png       # Alto DPI (4K)
├── logo-512x512.png       # Marketing / GitHub
├── favicon.ico            # Icone Windows (16+32+48)
└── logo.svg               # Vetorial original (manter)
```

---

## Especificacoes por Arquivo

### 1. logo-16x16.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 16 x 16 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | Title bar da janela, miniatura |
| **Design** | Apenas "DPI" ou icone abstrato |
| **Cores** | Fundo transparente, texto #0F172A |

---

### 2. logo-32x32.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 32 x 32 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | Taskbar Windows, Alt+Tab |
| **Design** | "DPI" com cores Cyan/Magenta |
| **Cores** | Fundo transparente, letters #00AEEF + #EC008C |

---

### 3. logo-48x48.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 48 x 48 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | Header do app, Dialog "Sobre" |
| **Design** | Circulo com "DPI" estilizado |
| **Cores** | Fundo #0F172A, texto #FFFFFF |

---

### 4. logo-64x64.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 64 x 64 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | Splash screen, Loading |
| **Design** | Logo completo "DPI Visual" |
| **Cores** | Fundo transparente, gradiente #00AEEF -> #EC008C |

---

### 5. logo-128x128.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 128 x 128 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | Dialog "Sobre", Instalador |
| **Design** | Logo "DPI" + "Tintas HP" |
| **Cores** | Fundo #0F172A, texto #FFFFFF, detalhes #00AEEF |

---

### 6. logo-256x256.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 256 x 256 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | Displays 4K, Retina, Marketing |
| **Design** | Logo completo com detalhes |
| **Cores** | Paleta completa CMYK + #0F172A |

---

### 7. logo-512x512.png

| Campo | Valor |
|-------|-------|
| **Tamanho** | 512 x 512 pixels |
| **Formato** | PNG-32 (transparencia) |
| **Uso** | GitHub, Documentacao, Marketing |
| **Design** | Logo high-res para impressao |
| **Cores** | Paleta completa CMYK + #0F172A |

---

### 8. favicon.ico

| Campo | Valor |
|-------|-------|
| **Tamanho** | 16x16 + 32x32 + 48x48 (combinados) |
| **Formato** | ICO (Windows Icon) |
| **Uso** | Icone do executavel (.exe) |
| **Design** | "DPI" estilizado |
| **Ferramenta** | https://convertio.co/ ou https://icoconvert.com/ |

---

## Design Base

### Para Tamanhos Pequenos (16-32px)

```
┌─────────┐
│  D P I  │
└─────────┘
```

- Letras simples, sem detalhes
- Contraste alto
- Fundo transparente

### Para Tamanhos Medios (48-128px)

```
┌─────────────────┐
│   ┌─────────┐   │
│   │   DPI   │   │
│   └─────────┘   │
│  Tintas HP      │
└─────────────────┘
```

- Circulo ou quadrado arredondado
- Texto "DPI" em destaque
- Subtitulo opcional

### Para Tamanhos Grandes (256-512px)

```
┌─────────────────────────┐
│                         │
│      DPI VISUAL         │
│    ┌─────────────┐      │
│    │  C  M  Y  K │      │
│    └─────────────┘      │
│      Tintas HP          │
│   Controle de Tintas    │
│                         │
└─────────────────────────┘
```

- Logo completo com todos os elementos
- Detalhes de gradiente
- Sombra sutil

---

## Cores Oficiais DPI Visual

| Cor | Hex | Uso |
|-----|-----|-----|
| Ciano DPI | #00AEEF | Logo principal |
| Magenta | #EC008C | Destaque |
| Yellow | #EAB308 | Detalhes |
| Black | #0F172A | Fundo, texto |
| White | #FFFFFF | Texto sobre fundo escuro |

---

## Ferramentas Recomendadas

| Ferramenta | Uso | Link |
|------------|-----|------|
| Figma | Design vetorial | figma.com |
| GIMP | Edicao de imagem | gimp.org |
| ConvertICO | PNG para ICO | convertico.com |
| ICOConvert | Multiplos tamanhos | icoconvert.com |
| Pillow | Geracao programatica | pip install Pillow |

---

## Observacoes

1. **Todos os PNGs devem ter fundo transparente**
2. **O favicon.ico deve conter 3 tamanhos**: 16x16, 32x32, 48x48
3. **Mantenha o logo.svg** como referencia vetorial
4. **Teste em diferentes fundos** (claro e escuro)
5. **Nao use texto menor que 8px** em logos pequenos
