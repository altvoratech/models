# Kilo Gateway — Browser de Modelos

Aplicação web para consultar, pesquisar e explorar modelos disponíveis no [Kilo Gateway](https://api.kilo.ai). Construída com **FastAPI** no backend e uma interface moderna com glassmorphismo, animações e visualizador JSON interativo.

---

## ✨ Features

- **Busca full-text** — pesquisa por nome, ID ou qualquer campo do modelo
- **Filtros por Modelo e Marca/Provedor** — dropdowns populados automaticamente via API
- **Debounce na pesquisa** — busca em tempo real enquanto você digita (350ms)
- **Visualizador JSON interativo** — coluna Raw com árvore colapsável, syntax highlighting e ações:
  - 🔽 Expand/Collapse por nível (▶/▼)
  - 📋 Copiar JSON formatado para o clipboard
  - 🔍 Strings longas truncadas com tooltip no hover
- **Cache server-side** — respostas do Kilo Gateway cacheadas por 60s
- **Design premium** — glassmorphismo, orbs animados, micro-animações, skeleton loading

## 📁 Estrutura do Projeto

```
models/
├── app.py              # Servidor FastAPI (endpoints + cache)
├── kilo_models.py      # Script CLI para download de modelos
├── requirements.txt    # Dependências Python
├── README.md
└── web/
    └── index.html      # Interface web (HTML + CSS + JS, single-file)
```

## 🛠️ Requisitos

- **Python 3.13+** (testado com Python 3.13.x no Windows)
- Dependências: `fastapi>=0.111`, `uvicorn[standard]>=0.30`

## ⚡ Início Rápido

### 1. Criar e ativar o virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 3. (Opcional) Configurar autenticação

Se o endpoint do Kilo Gateway exigir autenticação, defina a variável de ambiente:

```powershell
$env:KILO_API_KEY="SEU_TOKEN_AQUI"
```

### 4. Iniciar o servidor

```powershell
python -m uvicorn app:app --reload --port 8000
```

### 5. Acessar

Abra no navegador: **http://127.0.0.1:8000**

## 🌐 API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET`  | `/` | Página HTML com interface de pesquisa e filtros |
| `GET`  | `/api/models` | Retorna listas de `models` e `brands` para os seletores |
| `GET`  | `/api/search` | Pesquisa com filtros |

### Parâmetros de `/api/search`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `q` | string | — | Texto livre para busca full-text |
| `model` | string | — | Filtrar por modelo exato |
| `brand` | string | — | Filtrar por marca/provedor exato |
| `limit` | int | `200` | Limite máximo de resultados (máx: 2000) |
| `url` | string | `https://api.kilo.ai/api/gateway/models` | URL do endpoint do gateway |

### Exemplo de chamada

```
GET /api/search?q=gpt&brand=OpenAI&limit=50
```

## 🖥️ Script CLI

O script `kilo_models.py` permite baixar e salvar o JSON dos modelos diretamente pela linha de comando:

```powershell
python kilo_models.py --out modelos.json
```

## 🎨 Interface

A interface utiliza um design moderno com:

- **Glassmorphismo** — painéis com `backdrop-filter: blur` e bordas translúcidas
- **Orbs animados** — gradientes flutuantes no background
- **Tipografia** — Inter (texto) + JetBrains Mono (código) via Google Fonts
- **Tema adaptativo** — suporte a `prefers-color-scheme` (dark/light)
- **Responsivo** — grid adaptativo para mobile, tablet e desktop
- **Skeleton loading** — indicadores de carregamento com shimmer
- **Status LED** — pill com indicador visual animado (verde/amarelo/vermelho)

---

**Kilo Gateway · Pesquisa de Modelos · 2026**
