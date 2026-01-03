<!--
Issue template (draft). This file is a drafted issue describing
proposed features and which ones are new compared to the current
Mergington High School Activity System.
-->
# Propuesta: Nuevas características para el sistema de actividades

Resumen
--
Lista de características propuestas para ampliar `Mergington High School API` y cuáles serían nuevas respecto al estado actual del proyecto.

Características propuestas (relevantes para gestión de actividades)
- Autenticación y autorización: registro, login, roles (estudiante/teacher/admin).
- Persistencia: migrar de base en memoria a una base de datos (SQLite/Postgres).
- Límite de participantes: comprobaciones atómicas y cola de espera.
- Gestión avanzada de horarios: calendarios, integración iCal/Google Calendar.
- Búsqueda y filtros: por día, categoria, disponibilidad, profesor.
- Panel administrativo: CRUD para actividades, exportar participantes, informes.
- Notificaciones: emails o WebPush para confirmaciones y cambios de horario.
- API pública documentada (OpenAPI) y pruebas automáticas.
- Internacionalización (i18n) y formato regional de fechas/horarios.

Características del repositorio "FTC-Skystone" que NO aplican o serían opcionales
- Control de hardware (motores, sensores) — no aplicable.
- Visión por ordenador en tiempo real — opcional y avanzado.
- Entornos de programación visual (Block Programming) — no prioritario.

Prioridad recomendada
--
1. Autenticación y persistencia
2. Límite de participantes + cola de espera
3. Panel administrativo y exportación
4. Notificaciones y calendario
5. API/documentación y pruebas

Siguientes pasos sugeridos
- Revisar y aprobar la lista.
- Crear issues atómicos por cada característica prioritaria.
- Implementar una primera PR para añadir persistencia (SQLite) y migración de datos.

Etiqueta propuesta: enhancement, planning

--
Creado automáticamente como borrador por el asistente. Puedo abrir este contenido como un issue en GitHub si me das permiso/credenciales.
