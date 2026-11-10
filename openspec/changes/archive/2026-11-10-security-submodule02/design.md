## Context

El sistema BoletoYa completó el Submódulo 01 (Autenticación y Registro de Usuarios). La arquitectura establecida cuenta con separación estricta de responsabilidades (Router → Service → Repository en backend; Component → Store/Composable → Service en frontend).
En el estado actual, el modelo `User` posee una única columna `role` con valor por defecto `PASAJERO`, y la vista `DashboardView.vue` es una página monolítica básica para pasajeros sin navegación modular.

Este diseño define la solución técnica para el **Submódulo 02: Gestión de Usuarios, Roles y Permisos**, cumpliendo los requisitos funcionales RF-05, RF-07 y RF-08, respetando las convenciones arquitectónicas de `AGENTS.md` y las especificaciones de dominio de `PROJECT.md`.

## Goals / Non-Goals

**Goals:**
- Implementar visualización dinámica del dashboard y menú de navegación según los roles del usuario autenticado (RF-05, CP-23 a CP-27).
- Habilitar al Administrador General para asignar y revocar roles secundarios preservando de forma permanente el rol base "Pasajero" (RF-07, CP-28 y CP-29).
- Implementar la baja lógica (`is_active = false`) y rehabilitación de usuarios con retroalimentación explícita (RF-08, CP-30, CP-31, CP-32).
- Adaptar el modelo de datos a una relación N:M real entre usuarios y roles (`user_roles`).
- Incorporar control de acceso robusto en backend (HTTP 403 Forbidden centralizado en `permissions.py`) y en frontend (guards de navegación y filtrado de sidebar).
- Blindar la seguridad de la cuenta administrativa contra auto-baja y auto-revocación de privilegios.
- Proveer una tabla de gestión de usuarios con búsqueda por texto y paginación en el panel administrativo.
- Implementar pruebas unitarias en backend (pytest) y frontend (vitest) para casos de frontera, errores y seguridad.

**Non-Goals:**
- Implementación de la lógica funcional interna de los módulos diferentes a Usuarios (Cooperativas, Buses, Rutas, etc. mostrarán una vista en blanco informativa con el nombre del módulo).
- Gestión de usuarios por parte de `ADMIN_COOPERATIVA` (queda diferido para cuando se construya el módulo de Cooperativas).
- Creación manual de nuevos tipos de roles dinámicos en tiempo de ejecución (los roles son los 4 estipulados por el dominio).

## Decisions

### D1: Modelo de datos para roles — Tabla de asociación N:M (`user_roles`)

**Elección:** Crear una tabla relacional `user_roles` con clave primaria compuesta `(user_id, role)` y migrar la columna `role` existente en `users`.

```sql
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, role)
);
```

**Alternativas consideradas:**
- *Columna ARRAY de enum en PostgreSQL:* Menos portable, genera complicaciones con el mapeador ORM de SQLAlchemy y migraciones de Alembic en caso de añadir o ajustar enums.
- *Roles empaquetados en un campo JSONB:* Pierde integridad referencial a nivel de base de datos y complica consultas indexadas y restricciones de unicidad.

**Rationale:** Cumple cabalmente con la regla de `PROJECT.md` y CP-27 ("posesión de múltiples roles activos simultáneos"). La relación N:M es limpia, normalizada y escalable. En SQLAlchemy se modela mediante `relationship("UserRoleAssociation", back_populates="user")` o una tabla secundaria.

### D2: Verificación de roles en Backend contra la Base de Datos

**Elección:** La validación de roles en endpoints protegidos verifica los roles vigentes cargados desde la base de datos a través de la entidad `User` obtenida en la dependencia `get_current_user`. El JWT mantiene su función de identificar al sujeto (`sub = user.id`), pero no se utiliza como fuente de verdad inmutable de roles para autorizar operaciones sensibles.

**Alternativas consideradas:**
- *Roles leídos exclusivamente del payload del JWT:* Si a un usuario se le revoca un rol crítico mientras tiene una sesión activa, mantendría acceso indebido durante los 30 minutos de validez del token.

**Rationale:** La dependencia `get_current_user` ya realiza una consulta a PostgreSQL (`user_repo.get_by_id`) para validar la existencia y estado activo de la cuenta. Cargar la colección de roles en la misma transacción añade un costo despreciable y garantiza consistencia y seguridad inmediata.

### D3: Mapeo y Normalización de Roles y Enums

**Elección:** Unificar la nomenclatura del enum en el backend y frontend como:
- `ADMIN_GENERAL`
- `ADMIN_COOPERATIVA`
- `SECRETARIA_COOPERATIVA` (corrigiendo la discrepancia con `SECRETARIA` observada en el código inicial de SM01)
- `PASAJERO`

**Rationale:** Alinea la base de código directamente con la especificación de dominio `PROJECT.md` y los requerimientos `submodule02.md`.

### D4: Invariabilidad del Rol "Pasajero" y Auto-Protección del Administrador

**Elección:**
1. **Regla de Pasajero permanente:** Tanto a nivel de DTO (`schemas/user_schemas.py`) como de servicio (`UserService`), cualquier actualización de roles sobre un usuario inyectará y preservará obligatoriamente el rol `PASAJERO`, independientemente de lo que envíe el cliente. En el frontend, el checkbox de "Pasajero" permanece permanentemente marcado y deshabilitado (`disabled`).
2. **Auto-protección administrativa:** El servicio `UserService` valida `target_user.id != current_user.id` en las operaciones de cambio de rol y cambio de estado (`is_active`). En caso de coincidencia, se interrumpe la ejecución con `HTTP 403 Forbidden` y el mensaje `"No se permite modificar los roles o estado de la propia cuenta administrativa"`. En la UI, los botones de acción para la fila correspondiente al usuario autenticado se muestran deshabilitados.

### D5: Shell de Navegación del Dashboard, Rutas Hijas y Sidebar Responsive

**Elección:** Refactorizar la arquitectura de rutas del frontend transformando `DashboardView` en `DashboardLayout.vue` con un `<aside>` reactivo, colapsable en escritorio, con soporte de menú móvil drawer/overlay y un `<RouterView>` para el área principal.

**Estructura de módulos y visibilidad:**

| Módulo | Ruta | Roles autorizados | Estado en SM02 |
|---|---|---|---|
| Usuarios | `/dashboard/usuarios` | `ADMIN_GENERAL` | Vista funcional completa |
| Cooperativas | `/dashboard/cooperativas` | `ADMIN_GENERAL` | Vista placeholder |
| Rutas generales | `/dashboard/rutas-generales` | `ADMIN_GENERAL` | Vista placeholder |
| Precios generales | `/dashboard/precios-generales` | `ADMIN_GENERAL` | Vista placeholder |
| Rutas de cooperativa | `/dashboard/rutas-cooperativa` | `ADMIN_COOPERATIVA` | Vista placeholder |
| Buses | `/dashboard/buses` | `ADMIN_COOPERATIVA` | Vista placeholder |
| Turnos | `/dashboard/turnos` | `ADMIN_COOPERATIVA` | Vista placeholder |
| Tarifas específicas | `/dashboard/tarifas` | `ADMIN_COOPERATIVA` | Vista placeholder |
| Reservas | `/dashboard/reservas` | `SECRETARIA_COOPERATIVA`, `PASAJERO` | Vista placeholder |
| Perfil | `/dashboard/perfil` | `PASAJERO` | Vista placeholder |

Cuando un usuario posee roles combinados (ej. `ADMIN_COOPERATIVA` y `PASAJERO`), el sidebar computa la unión matemática de los módulos permitidos (CP-27). La Secretaria de Cooperativa centraliza sus actividades de cobro y reservas en el módulo "Reservas".

**Comportamiento de Interfaz Responsive y Colapso:**
- **Escritorio (≥ md):** La barra lateral incluye un botón de alternancia (*toggle*) que permite contraer el sidebar a un ancho compacto (`w-16` / `w-20` mostrando únicamente los iconos centrados con tooltips) o expandirlo al ancho estándar (`w-64` mostrando icono y nombre completo del módulo).
- **Móviles y pantallas pequeñas (< md):** Se incorpora un botón de menú hamburguesa en el header principal que abre un drawer/overlay flotante con backdrop difuminado, permitiendo el acceso completo a los módulos autorizados y cerrándose automáticamente al seleccionar una ruta o pulsar el botón de cierre.

### D6: Consulta Paginada con Búsqueda Insensible a Mayúsculas/Minúsculas

**Elección:** El endpoint `GET /api/v1/usuarios` implementa los parámetros:
- `page` (entero ≥ 1, default 1)
- `size` (entero entre 1 y 100, default 10)
- `search` (cadena opcional)
- `include_inactive` (booleano, default false)

Retorna una estructura con metadatos:
```json
{
  "items": [ ... ],
  "total": 45,
  "page": 1,
  "size": 10,
  "pages": 5
}
```
En el frontend se implementa debounce de 300 ms en el campo de búsqueda para optimizar las peticiones de red.

## Architecture & Layering

Siguiendo las directrices obligatorias de `AGENTS.md`:

### Backend Flow
```
UserRouter (FastAPI) 
  → Depends(require_role("ADMIN_GENERAL"))
  → UserService (validaciones de negocio, permisos, consistencia)
  → UserRepository (SQLAlchemy query, joins, ilike, pagination)
  → PostgreSQL
```

- **Router (`api/v1/users_router.py`):** Sin lógica de negocio ni consultas directas a base de datos.
- **Service (`services/user_service.py`):** Encargado de forzar la presencia de `PASAJERO`, evitar auto-desactivación, controlar transiciones de estado válidas y formatear DTOs.
- **Repository (`repositories/user_repository.py`):** Manejo de sesiones y consultas con filtros `ilike` sobre nombre, apellido y email.

### Frontend Flow
```
UsersView.vue (Template + Lucide Icons)
  → users.store.ts / composable (estado reactivo, paginación, filtros)
  → users.service.ts (HTTP client tipado)
  → REST API (/api/v1/usuarios)
```

## UI/UX & Design Guidelines

- **Componentes:** Integración de componentes shadcn-vue existentes y estilos Tailwind basados en tokens del tema Soft Pop (`bg-card`, `text-card-foreground`, `border-border`, `bg-primary`, etc.).
- **Iconografía:** Prohibido el uso de emojis en toda la interfaz. Utilización exclusiva de `@lucide/vue`:
  - `Users`, `UserCheck`, `UserX`, `Shield`, `Search`, `ChevronLeft`, `ChevronRight`, `AlertCircle`, `CheckCircle2`, `SlidersHorizontal`.
- **Accesibilidad y feedback:**
  - Badges semánticos para roles y estado: verde tenue para `Activo`, gris/rojo tenue para `Inactivo`.
  - Diálogos modales con soporte para tecla `Escape` y foco controlado para confirmación de baja/habilitación y asignación de roles.
  - Indicadores visuales de carga en botones (`Loader2` animado).

## Automated Testing Strategy

Siguiendo el requerimiento de implementar pruebas unitarias que cubran casos diferentes a los CPs ejecutados manualmente:

### Backend Tests (pytest)
- **`test_user_service_limits.py`:**
  - Búsqueda con cadenas vacías o términos sin coincidencias (`search="@@@noexiste"`).
  - Paginación fuera de rango (`page=999`).
  - Validación de esquemas Pydantic con tamaños inválidos (`size=0`, `size=-5`).
  - Intento de auto-desactivación por el propio administrador logueado (retorna 403).
  - Intento de auto-revocación del rol ADMIN_GENERAL por el propio administrador (retorna 403).
  - Intento de desactivar un usuario ya inactivo (retorna 400 Bad Request).
  - Intento de habilitar un usuario ya activo (retorna 400 Bad Request).
  - Asignación de lista vacía de roles: debe forzar automáticamente `[PASAJERO]`.
  - Asignación de roles duplicados en payload: debe persistir sin duplicados en DB.
- **`test_permissions_middleware.py`:**
  - Evaluación de usuarios con combinaciones de múltiples roles ante diferentes restricciones.
  - Verificación de respuesta HTTP 403 con payload JSON estructurado.

### Frontend Tests (vitest)
- **`DashboardLayout.spec.ts`:**
  - Computación de módulos visibles para combinaciones no estándar de roles.
  - Manejo graceful cuando el usuario no posee roles o el arreglo está vacío.
- **`UsersView.spec.ts`:**
  - Deshabilitación de botones de acción en la fila coincidente con el ID del usuario en sesión.
  - Estado `disabled` y `checked` inmutable del checkbox "Pasajero" en el modal de asignación.
  - Reseteo de número de página a 1 cuando cambia el criterio de búsqueda.
- **`router.spec.ts`:**
  - Redirección a `/dashboard` ante intento de acceso a `/dashboard/usuarios` por parte de un usuario con rol exclusivo `PASAJERO` o `ADMIN_COOPERATIVA`.

