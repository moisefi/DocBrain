# Security

DocBrain maneja documentacion interna y debe tratar la seguridad como requisito
de producto, no como capa opcional.

## Principios

- Multi-tenant obligatorio.
- Minimo privilegio.
- Secrets solo por variables de entorno o gestor de secretos.
- Auditoria de acciones sensibles.
- Validacion estricta de entrada.
- No registrar secretos ni contenido sensible innecesario.

## Autenticacion

- Password hashing con Argon2id.
- Access tokens JWT de vida corta.
- Refresh tokens rotatorios.
- Deteccion de reutilizacion de refresh token.
- Revocacion de familia de tokens ante compromiso.
- Rate limiting en login, refresh y endpoints costosos.

## Autorizacion

Cada caso de uso recibe un `TenantContext` con:

- `user_id`
- `organization_id`
- roles
- permisos derivados
- `correlation_id`

Ningun endpoint debe aceptar recursos tenant-scoped sin comprobar que pertenecen
a la organizacion activa.

## Aislamiento multi-tenant

- `organization_id` obligatorio en tablas compartidas.
- Filtros por tenant en repositorios.
- Tests de acceso cruzado entre organizaciones.
- Auditoria de accesos denegados relevantes.
- Indices compuestos que incluyan `organization_id` donde aplique.

## Seguridad documental

- Allowlist de MIME types.
- Limite de tamano por archivo.
- Hash de contenido para deduplicacion y trazabilidad.
- Nombres de archivo tratados como datos no confiables.
- Extraccion en workers, fuera del request principal.
- Borrado logico inicial para conservar auditoria.

## Seguridad LLM

- Documentos recuperados se tratan como datos no confiables.
- Mitigaciones de prompt injection.
- Separacion clara de instrucciones y contexto.
- Prohibido exponer prompts internos, claves o configuracion.
- Respuestas abstienen cuando falta evidencia.
- Citas obligatorias para afirmaciones basadas en documentos.

## OWASP

Referencias iniciales:

- OWASP ASVS para autenticacion, sesiones y autorizacion.
- OWASP API Security Top 10.
- OWASP LLM Top 10 para riesgos especificos de IA.

## Auditoria minima

- Login y logout.
- Fallos repetidos de autenticacion.
- Reutilizacion de refresh token.
- Cambios de roles.
- Subida, borrado y reingestion de documentos.
- Consultas RAG.
- Accesos denegados por tenant o permisos.

