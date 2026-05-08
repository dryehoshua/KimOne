# Kim Live API Bridge Spec

Fecha: 2026-05-08.
Tarea: KIM-0034 / KIM-0035.

## Objetivo

Preparar a Kim Live para leer y modificar informacion viva de ClickUp y Notion desde una conversacion, sin depender solo de snapshots ni de una ejecucion manual posterior de Codex.

## Regla de seguridad

Kim puede leer estado en vivo sin confirmacion adicional. Para cualquier escritura debe seguir este flujo:

1. Preparar la accion con `confirm=false`.
2. Explicar al doctor que va a cambiar.
3. Esperar confirmacion explicita.
4. Ejecutar la accion con `confirm=true`.
5. Esperar respuesta de la API.
6. Guardar evidencia en memoria y responder si la API confirmo o fallo.

## Herramienta Realtime

Kim Live expone la herramienta `kim_api_bridge` al modelo Realtime.

Entrada:

```json
{
  "provider": "clickup",
  "action": "update_task",
  "parameters": {
    "task_id": "abc123",
    "fields": {
      "status": "in progress"
    }
  },
  "confirm": false
}
```

## ClickUp

Credencial:

```text
service: codex.clickup.personal_token
account: dryehoshuapython
```

Acciones activas:

- `status`: valida conexion y usuario.
- `inventory`: lee equipos/workspaces.
- `list_spaces`: lista Spaces por workspace/equipo.
- `list_folders`: lista Folders dentro de un Space por `space_id` o `space_name`.
- `list_lists`: lista Lists dentro de un Folder o Lists directas de un Space.
- `list_tasks`: lista tareas de una lista por `list_id`; si no recibe `list_id`, devuelve snapshot local.
- `get_task`: lee una tarea por `task_id`.
- `create_folder`: crea un Folder en un Space, requiere confirmacion.
- `create_list`: crea una List dentro de un Folder o directa en un Space, requiere confirmacion.
- `create_task`: crea tarea en una lista, requiere confirmacion.
- `update_task`: actualiza campos de una tarea, requiere confirmacion.
- `comment_task`: comenta una tarea, requiere confirmacion.

Uso operativo: si Kim no conoce el `list_id`, ya no debe detenerse. Primero debe usar `list_spaces`, luego `list_folders` y `list_lists`. Si la estructura no existe, puede preparar `create_folder` o `create_list` con `confirm=false` y esperar confirmacion.

## Notion

Kim Live puede usar Notion directamente cuando exista un token de integracion en Keychain:

```text
service: codex.notion.integration_token
account: dryehoshuapython
```

Estado al 2026-05-06:

- Token directo guardado en Keychain.
- `/api/api-bridge/status` valida la integracion `KimOne` en el workspace `Ai People`.
- Las busquedas devuelven vacio hasta que el doctor comparta paginas/bases con la integracion.
- Prueba con `Kim - Centro de Trabajo` devolvio 404 con indicacion de compartir la pagina/base con la integracion `KimOne`.

Acciones preparadas:

- `status`: valida si hay token y, si existe, consulta usuario/bot.
- `search`: busca paginas o bases de datos.
- `get_page`: obtiene una pagina por `page_id`.
- `create_page`: crea una pagina bajo `parent_page_id` o `parent_database_id`, requiere confirmacion.
- `update_page_properties`: actualiza propiedades, requiere confirmacion.

Nota: Codex Desktop ya tiene acceso Notion por MCP, pero ese acceso vive en esta sesion de Codex, no dentro del servidor local de Kim Live. Para que Kim Live opere Notion sola, se necesita token de integracion Notion o un worker remoto con acceso MCP.

## Sonido de operacion

Kim Live usa un tono tipo caja musical mientras interactua con ClickUp/Notion. El tono de investigacion web queda separado como sonido de cuenco.

## Evidencia y memoria

Cada accion del bridge queda registrada en:

```text
BIFROST/MEMORY/context/api_bridge_actions.jsonl
```

Tambien se agrega una nota diaria y un evento en el inbox de Kim Live.
