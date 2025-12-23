
# Backend - SuperCarros Republishing Scheduler

## Requisitos

- Python 3.10+
- MySQL (gestionable con MySQL Workbench)
- Playwright

## Instalación

```bash
cd backend
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install -r requirements.txt

# Instalar navegadores de Playwright
playwright install
```

Configura tu base de datos editando `app/core/config.py` o usando un archivo `.env`.

## Ejecutar

```bash
uvicorn app.main:app --reload
```

La API estará en `http://localhost:8000`.
