# ADR-0001: Monolito modular

## Estado

Aceptado.

## Contexto

DocBrain combina API SaaS, autenticacion, multi-tenancy, ingestion documental,
retrieval, llamadas LLM, auditoria y observabilidad.

Separar el sistema en microservicios desde el inicio aumentaria la complejidad
operacional antes de validar el producto y el pipeline RAG.

## Decision

Se adopta un monolito modular con limites internos por modulo y capas:

- API.
- Application.
- Domain.
- Infrastructure.

Los modulos no deben acceder directamente a detalles internos de otros modulos.
La comunicacion se realiza mediante casos de uso, puertos o eventos internos
cuando sea necesario.

## Alternativas consideradas

### Microservicios

Rechazado para el MVP por coste operacional, complejidad de despliegue,
observabilidad distribuida y coordinacion de transacciones.

### Monolito sin modularidad

Rechazado porque mezclaria endpoints, reglas de negocio, SQL y llamadas LLM,
reduciendo mantenibilidad y testabilidad.

## Consecuencias

Positivas:

- Desarrollo inicial mas rapido.
- Menos infraestructura.
- Transacciones y tests de integracion mas simples.
- Refactorizacion futura mas controlada si los limites se respetan.

Negativas:

- Requiere disciplina para evitar acoplamiento interno.
- Escalado independiente limitado.
- Los jobs pesados deben aislarse mediante workers para no afectar la API.

## Reglas de implementacion

- FastAPI no contiene reglas de negocio.
- Los casos de uso coordinan transacciones y permisos.
- El dominio no importa frameworks.
- Repositorios y clientes externos viven en infraestructura.
- Las dependencias entre modulos deben ser explicitas.

