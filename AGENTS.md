# AGENTS.md — BoletoYa

Instrucciones para agentes de IA trabajando en este repositorio.
Contexto de dominio (roles, reglas de negocio, UI/UX) está en `PROJECT.md` — léelo también antes de implementar.

## Stack

- Frontend: Vue 3 + TypeScript (`<script setup lang="ts">`), Pinia
- Backend: FastAPI + Python, SQLAlchemy, PostgreSQL
- API: REST, JSON, versionada bajo `/api/v1/...`

## Comandos

```bash
# Backend
uvicorn app.main:app --reload        # dev server
pytest                               # tests
alembic upgrade head                 # migraciones

# Frontend
npm run dev                          # dev server
npm run test:unit                    # component/store/composable tests
npm run lint                         # lint + type check
```

## Arquitectura (obligatoria)

```
Frontend: Vue Component → Store/Composable → API Service → REST API
Backend:  Router → Service → Repository → PostgreSQL
```

Reglas:
- Los **routers** de FastAPI solo reciben input, llaman a un Service y devuelven output. Nunca `db.query()` ni SQL directo en el router.
- La **lógica de negocio** vive en Services (ej: verificar disponibilidad de asiento, validar transición de estado, cancelar reserva). 
- El acceso a PostgreSQL vive únicamente en **Repositories**.
- Los **componentes Vue** no hacen llamadas HTTP directas ni contienen lógica de negocio; eso va en `services/*.service.ts` y composables.

Ejemplo de flujo:
```
ReservaRouter → ReservaService → ReservaRepository → PostgreSQL
```

## Convenciones de código 

```python
# DTOs separados por operación
class ReservaCreate(BaseModel): ...
class ReservaUpdate(BaseModel): ...
class ReservaResponse(BaseModel): ...
# Nunca devolver el modelo ORM directamente al cliente
```

```typescript
// Llamadas HTTP centralizadas en services/, nunca en componentes
// services/reserva.service.ts
export async function crearReserva(data: ReservaCreate) { ... }
```

- TypeScript estricto, evitar `any` sin justificación.
- Inyección de dependencias vía `Depends` de FastAPI (sesión de DB, usuario autenticado, roles), no instanciar manualmente.
- Nuevos endpoints van bajo `/api/v1/<recurso>`, organizados con `APIRouter`, nunca todo en `main.py`.

## Diseño visual

El proyecto utiliza shadcn-vue y el tema Soft Pop generado con tweakcn:

- Tema: https://tweakcn.com/editor/theme?theme=soft-pop
- Componentes shadcn-vue: https://shadcn-vue.com/docs/components

### Reglas al implementar interfaz de usuario

- Reutiliza los componentes disponibles de shadcn-vue antes de crear componentes personalizados.
- Mantén el tema Soft Pop existente y utiliza sus tokens semánticos para los estilos de la interfaz.
- La fuente de verdad del tema visual es `frontend/src/assets/css/index.css`.
- No modifiques los tokens globales del tema a menos que la tarea requiera explícitamente un cambio en el sistema de diseño.
- No introduzcas otra biblioteca de componentes de UI sin autorización expresa.
- No utilices colores hardcodeados (`hex`, `rgb`, `hsl`, `oklch`, etc.) cuando exista un token semántico equivalente.
- Prefiere las clases semánticas de Tailwind proporcionadas por el tema, por ejemplo: `bg-primary`, `text-primary-foreground`, `bg-background`, `text-foreground`, `border-border`, etc.
- Mantén la compatibilidad con los modos claro y oscuro al implementar nuevos componentes.
## Clean Code — 9 principios
 
### 1. Nombres significativos
Nombrar variables y funciones para revelar su propósito, no solo su valor.
```python
# ❌ n = 24
# ✅ age_in_months = 24
```
 
### 2. Una función, una responsabilidad
Separar cada responsabilidad en una función independiente.
```python
# ❌
def handle_user():
    save_user()

def save_user():
    validate_user()
    save_to_db() 

# ✅
def handle_user():
    validate_user()
    save_user()

def validate_user():
    # validar usuario

def save_user():
    # guardar usuario

```
 
### 3. Evitar números mágicos
Reemplazar valores codificados con constantes con nombre.
```python
# ❌
if score > 65:
    return "Pass"
 
# ✅
PASSING_SCORE = 65
if score > PASSING_SCORE:
    return "Pass"
```
 
### 4. Usar booleanos descriptivos
Los nombres de booleanos deben indicar una condición, no solo un valor.
```python
# ❌ if flag: ...
# ✅ if user.can_access_account: ...
# ✅ if password_is_too_short: ...
```
 
### 5. DRY (Don't Repeat Yourself)
Código duplicado significa errores duplicados. Reutilizar lógica donde tenga sentido.
```python
# ❌ Repetir el mismo mensaje de bienvenida en 3 lugares distintos
 
# ✅
def greet_user(username: str) -> str:
    return f"Welcome, {username}!"
```
 
### 6. Evitar el anidamiento profundo
Aplanar el flujo del código para mejorar la claridad.
```python
# ❌
if user:
    if user.is_active:
        if user.has_permission():
            do_task()
 
# ✅
if not user or not user.is_active or not user.has_permission():
    return
do_task()
```
 
### 7. Comentar el por qué, no el qué
Explicar la intención detrás del código, no la mecánica obvia.
```python
# ❌ # increment i
i += 1
 
# ✅ # Skip the first item (header row)
i += 1
```
 
### 8. Limitar los argumentos de las funciones
Demasiados parámetros confunden. Agrupar datos relacionados en objetos/DTOs.
```python
# ❌ def create_user(a, b, c, d, e): ...
 
# ✅
def create_user(user_data: UserCreate): ...
```
 
### 9. Código autoexplicativo
El código bien escrito necesita menos comentarios porque se lee como una historia.
```python
# ❌
def du(u):
    return u.r if u.s else None
 
# ✅
def get_user_role(user: User) -> str | None:
    return user.role if user.is_signed_in else None
```

## Permisos centralizados (`permissions.py`)
 
Nunca repetir checks de rol/pertenencia inline en cada router. Centralizar en un módulo `permissions.py` y usarlo vía `Depends`.
 
```python
# app/core/permissions.py
from fastapi import Depends, HTTPException, status
 
def require_role(*roles: str):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No autorizado")
        return current_user
    return checker
 
def require_own_cooperativa(current_user: User = Depends(get_current_user)):
    def checker(cooperativa_id: int):
        if current_user.role == "ADMIN_COOPERATIVA" and current_user.cooperativa_id != cooperativa_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Recurso de otra cooperativa")
    return checker
```
 
```python
# ✅ Uso en el router
@router.post("/rutas")
def crear_ruta(
    data: RutaCreate,
    user: User = Depends(require_role("ADMIN_GENERAL", "ADMIN_COOPERATIVA")),
):
    ...
```
 
```python
# ❌ Evitar checks de rol repetidos e inline en cada endpoint
if current_user.role != "ADMIN_GENERAL" and current_user.role != "ADMIN_COOPERATIVA":
    raise HTTPException(403)
```
 
Toda nueva regla de autorización (rol nuevo, permiso nuevo, verificación de pertenencia) se agrega en `permissions.py`, nunca duplicada en routers o services.
 
## Variables de entorno (`.env`)
 
Todas las variables sensibles o de configuración se centralizan en `.env`, nunca hardcodeadas en el código.
 
```bash
# .env (nunca commitear; usar .env.example como plantilla)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```
 
```python
# app/core/config.py — punto único de acceso, vía pydantic-settings
from pydantic_settings import BaseSettings
 
class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
 
    class Config:
        env_file = ".env"
 
settings = Settings()
```
 
```python
# ✅ Import settings, no os.getenv() disperso por el código
from app.core.config import settings
jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
 
# ❌ Evitar
SECRET = "hardcoded-secret-123"
os.getenv("JWT_SECRET_KEY")  # disperso en múltiples archivos
```
 
Mantener un `.env.example` versionado (sin valores reales) para que cualquier dev/agente sepa qué variables se necesitan.

## Boundaries (no hacer)

- No agregar dependencias nuevas si no son estrictamente necesarias.
- No modificar la arquitectura por capas sin justificación explícita.
- No mostrar errores técnicos/stack traces al usuario final.
- No loguear contraseñas, tokens, ni datos de pago.
- No confiar en validaciones hechas solo en el frontend (especialmente disponibilidad de asientos).

## Antes de implementar

1. Revisar módulo existente (Seguridad / Cooperativas / Reservas) y reutilizar Services/Repositories/composables ya creados.
2. Revisar `PROJECT.md` para reglas de roles, estados y permisos del dominio.
3. Validar autenticación/autorización (rol + pertenencia a cooperativa) antes de operaciones protegidas.
4. Añadir o actualizar tests para el caso implementado.
5. Ante conflicto entre "rápido" y "arquitectónicamente correcto", gana la arquitectura.

## Criterio de "hecho"

- [ ] Sigue Router → Service → Repository (o Component → Store/Composable → API Service)
- [ ] Tipado completo (Pydantic / TypeScript), sin `any` injustificado
- [ ] Roles y pertenencia a cooperativa validados donde aplique
- [ ] Tests añadidos para el caso crítico (reservas, asientos, roles)
- [ ] Sin secretos ni datos sensibles en código o logs