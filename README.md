# BoletoYa

Aplicación de gestión de cooperativas, usuarios, localidades y rutas de transporte. Frontend con Vue 3, TypeScript y Pinia; backend con FastAPI, SQLAlchemy y PostgreSQL.

## 1. Requisitos

- Git 2.40 o superior.
- Python 3.14 con pip y venv.
- Node.js `^22.18.0` o `>=24.12.0`, con npm.
- PostgreSQL 16 o superior, iniciado y con `psql` disponible.

Los comandos siguientes utilizan PowerShell.

## 2. Clonar el repositorio

```powershell
git clone https://github.com/ByronJ005/TIC-2026.git
cd TIC-2026
```

## 3. Configurar el backend

Desde la raíz del proyecto:

```powershell
cd backend
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

Cree la base de datos si todavía no existe:

```powershell
psql -h localhost -U postgres -W -c "CREATE DATABASE boletoya_db;"
```

Edite `backend/.env` con sus credenciales y un secreto JWT propio:

```dotenv
DATABASE_URL=postgresql://USUARIO:CLAVE@localhost:5432/boletoya_db
JWT_SECRET_KEY=REEMPLAZAR_POR_UN_SECRETO_ALEATORIO
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5173
```

Las demás variables están en [backend/.env.example](backend/.env.example). Configure SMTP para recuperación de contraseñas y correos. No publique `.env`.

Aplique las migraciones desde `backend`:

```powershell
python -m alembic upgrade head
```

## 4. Configurar el frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
npm ci
```

La API predeterminada es `http://localhost:8000/api/v1`. Para cambiarla, defina `VITE_API_URL` en `frontend/.env.local`.

## 5. Inicializar datos

| Archivo | Contenido |
| --- | --- |
| [backend/data/seed_users.py](backend/data/seed_users.py) | Crea o actualiza usuarios y roles de prueba. |
| [backend/data/seed_localities.py](backend/data/seed_localities.py) | Carga las localidades faltantes. |
| [backend/data/localities_loja.json](backend/data/localities_loja.json) | Catálogo de 123 localidades, sin El Cisne. |

Desde `backend`, con el entorno virtual activo y las migraciones aplicadas:

```powershell
python -m data.seed_users
python -m data.seed_localities
```

## 6. Ejecutar la aplicación

**Terminal 1 — desde la raíz:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — desde la raíz:**

```powershell
cd frontend
npm run dev -- --host localhost --port 5173 --strictPort
```

- Aplicación: [http://localhost:5173](http://localhost:5173)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Estado de la API: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

## 7. Pruebas y compilación

Desde `backend`, con el entorno virtual activo:

```powershell
python -m pytest
```

Desde `frontend`:

```powershell
npm run test:unit -- --run
npm run type-check
npm exec -- oxlint .
npm exec -- eslint .
npm run build
```

La compilación genera `frontend/dist`.
