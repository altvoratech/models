# Kilo Gateway — Browser de Modelos (FastAPI)

Projeto simples para consultar o endpoint do Kilo Gateway e navegar/pesquisar modelos via uma página HTML.

## Requisitos

- Python 3.13+ (testado com Python 3.13.x no Windows)

## Configuração

1) (Opcional) Defina o token do Kilo:

PowerShell:
```powershell
$env:KILO_API_KEY="SEU_TOKEN"
```

2) Instale dependências:
```powershell
python -m pip install -r requirements.txt
```

> Observação: se você estiver usando um venv local, ative-o antes de instalar.

## Executar

Subir o servidor:
```powershell
python -m uvicorn app:app --reload --port 8000
```

Acessar:
- `http://127.0.0.1:8000/`

## Endpoints

- `GET /` — página HTML (pesquisa + filtros)
- `GET /api/models` — retorna listas de `models` e `brands` para popular os seletores
- `GET /api/search?q=...&model=...&brand=...&limit=...` — pesquisa completa + filtros

## Script CLI (opcional)

Também existe o script `kilo_models.py` para baixar e imprimir o JSON do endpoint:

```powershell
python kilo_models.py --out modelos.json
```

