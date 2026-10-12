## Context

BoletoYa es una app web de reserva de boletos de transporte terrestre. El proyecto tiene la estructura de capas definida (Router → Service → Repository) pero todas las carpetas del backend están vacías. No existe modelo de usuario, autenticación, ni protección de endpoints. El frontend tiene Vue 3 + Pinia + Vue Router configurados con shadcn-vue y Tailwind, pero sin páginas ni stores funcionales.

Este diseño cubre el submódulo 01 de Seguridad: registro, login y logout. Es el primer código funcional del proyecto.

**Stack existente relevante:**
- Backend: FastAPI, SQLAlchemy, Alembic, python-jose, passlib + bcrypt, pydantic-settings
- Frontend: Vue 3 (rc) + TypeScript, Pinia 4, Vue Router 5, Vite, shadcn-vue, Vitest
- DB: PostgreSQL (local)

## Goals / Non-Goals

**Goals:**
- Implementar RF-01 (Registro), RF-02 (Login), RF-04 (Logout) del spec `submodule01.md`.
- Cumplir los 17 CPs definidos: validaciones de cédula ecuatoriana, pasaporte, email, contraseña, campos vacíos, normalización de email, protección de rutas, logout multi-pestaña.
- Establecer la infraestructura base que otros módulos reutilizarán: modelo User, JWT, dependency `get_current_user`, navigation guards, store de autenticación.
- Automatizar ~13 tests backend + ~7 tests frontend para las capas internas.

**Non-Goals:**
- Recuperación de contraseña (RF-03 probable, otro submódulo).
- Bloqueo de cuenta por intentos fallidos.
- Refresh tokens / sesiones de larga duración.
- Dashboards funcionales por rol (solo placeholder de PASAJERO).
- Verificación de email (envío de correo de confirmación).
- OAuth / login social.
- Gestión de usuarios desde panel admin (otro módulo).

## Decisions

### D1: JWT con blacklist para invalidación en logout

**Elección:** Access token JWT de 30 minutos + tabla `blacklisted_tokens` en PostgreSQL para invalidar tokens en logout.

**Alternativas consideradas:**
- *JWT stateless puro:* No cumple CP-15/CP-16/CP-17 porque el token sigue válido tras logout hasta que expira.
- *Sesiones server-side (cookie + DB):* Cumple todo pero contradice PROJECT.md ("Autenticación basada en JWT") y la arquitectura REST stateless.
- *JWT + Redis para blacklist:* Óptimo en escala, pero añade dependencia de infraestructura innecesaria para la escala de BoletoYa.

**Rationale:** La blacklist en PostgreSQL es simple (tabla con `jti` y `expires_at`), no requiere infraestructura adicional, y permite invalidación inmediata. El overhead de un lookup por request es despreciable con un índice en `jti`. Los tokens expirados se limpian periódicamente.

**Payload del JWT:**
```json
{
  "sub": "<user_id>",
  "role": "<role>",
  "jti": "<uuid>",
  "exp": "<timestamp>"
}
```

### D2: Hash de contraseñas con bcrypt

**Elección:** bcrypt vía `passlib[bcrypt]` con work factor 12.

**Alternativas consideradas:**
- *argon2:* Más moderno (ganador PHC) pero requiere nueva dependencia. AGENTS.md: "no agregar dependencias nuevas si no son estrictamente necesarias".
- *scrypt:* Disponible en stdlib, pero menos ergonómico y sin passlib CryptContext.

**Rationale:** passlib y bcrypt ya están en `requirements.txt`. bcrypt con factor 12 es el estándar de la industria y perfectamente seguro para producción.

### D3: Validaciones duplicadas con constantes bien definidas

**Elección:** Mismas reglas de validación implementadas en Pydantic (backend) y en un composable Vue (frontend). Backend es la autoridad final.

**Alternativas consideradas:**
- *Schema compartido (JSON Schema):* DRY pero complejidad alta para generar validators en ambos lenguajes.
- *Solo backend:* Mala UX, el usuario no recibe feedback hasta el submit.

**Rationale:** Las validaciones frontend son para UX (feedback inmediato). El backend siempre valida (AGENTS.md: "no confiar en validaciones hechas solo en el frontend"). Las reglas están bien definidas y son estables, el riesgo de divergencia es bajo y se mitiga con tests que cubren los mismos inputs en ambos lados.

### D4: Tipos de documento — Cédula y Pasaporte

**Elección:** Enum `CEDULA` | `PASAPORTE`. La cédula se valida con el algoritmo de módulo 10 de la cédula ecuatoriana (10 dígitos). El pasaporte se valida como alfanumérico (6-20 caracteres).

### D5: Registro asigna PASAJERO siempre

**Elección:** El endpoint `POST /register` siempre asigna `role = "PASAJERO"`. El campo `role` no es aceptado en el DTO de entrada. Los demás roles se crean desde funcionalidad administrativa futura.

### D6: Email UNIQUE + Documento UNIQUE

**Elección:** Constraints UNIQUE en la tabla `users` para `email` y para la combinación `(document_type, document_number)`. Esto permite que una cédula "1234567890" y un pasaporte "1234567890" sean registros distintos (mismo número, diferente tipo).

### D7: HTTP client — fetch nativo con wrapper tipado

**Elección:** Usar `fetch` nativo envuelto en un service con tipado TypeScript, en lugar de añadir axios.

**Rationale:** AGENTS.md dice evitar dependencias innecesarias. `fetch` es nativo, el proyecto no necesita interceptors complejos de axios. Un wrapper simple (`apiClient`) centraliza headers (Authorization), manejo de errores (401 → logout), y base URL.

### D8: Estructura de archivos

```
backend/src/
├── api/
│   └── v1/
│       ├── __init__.py
│       └── auth_router.py
├── core/
│   ├── __init__.py
│   ├── config.py          # Settings (pydantic-settings)
│   ├── database.py        # Engine, SessionLocal, Base
│   ├── security.py        # hash, verify, create_token, decode_token
│   ├── dependencies.py    # get_db, get_current_user
│   └── permissions.py     # require_role (para uso futuro)
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── blacklisted_token.py
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py
│   └── token_repository.py
├── schemas/
│   ├── __init__.py
│   ├── user_schemas.py
│   └── auth_schemas.py
├── services/
│   ├── __init__.py
│   └── auth_service.py
└── main.py

frontend/src/
├── composables/
│   └── useFormValidation.ts
├── services/
│   ├── api-client.ts       # fetch wrapper con auth header
│   └── auth.service.ts
├── stores/
│   └── auth.store.ts
├── views/
│   ├── LoginView.vue
│   ├── RegisterView.vue
│   └── DashboardView.vue
└── router/
    └── index.ts            # (actualizado con rutas y guards)
```

### D9: Flujo post-registro

Tras registro exitoso: mostrar toast "Cuenta creada satisfactoriamente" → redirigir a `/login` después de ~2 segundos.

### D10: Mensajes de error de autenticación

Login con credenciales incorrectas devuelve un mensaje genérico "Credenciales incorrectas" sin revelar si el email existe o no (prevención de user enumeration). Registro con email/documento duplicado sí indica cuál campo está duplicado (es información necesaria para el usuario).

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| **Blacklist crece indefinidamente** → La tabla acumula tokens expirados | Agregar un job/script para limpiar tokens donde `expires_at < now()`. Fuera del alcance de este cambio pero trivial de implementar después. |
| **Divergencia de validaciones front/back** → Una regla se actualiza en un lado y no en el otro | Tests automatizados cubren los mismos inputs en ambos lados. Las reglas están centralizadas en constantes/regex nombradas. |
| **passlib en mantenimiento mínimo** → Posible deprecación futura | bcrypt funciona independientemente. Si passlib se abandona, migrar a `bcrypt` directo es un cambio de 1 archivo (`security.py`). |
| **Vue rc + Pinia 4** → APIs pueden cambiar antes del release estable | Bajo riesgo: las APIs de composición y stores son estables. Los overrides en `package.json` ya manejan esto. |
| **Token en localStorage** → Vulnerable a XSS | Mitigación estándar: sanitizar inputs, Content-Security-Policy headers (futuro). Para httpOnly cookies se necesita cambio de arquitectura (fuera de scope). |
