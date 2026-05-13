# Kim Live API Bridge Spec

Fecha: 2026-05-08.
Tarea: KIM-0034 / KIM-0035.

## Objetivo

Preparar a Kim Live para leer y modificar informacion viva de ClickUp y Notion desde una conversacion, sin depender solo de snapshots ni de una ejecucion manual posterior de Codex.

Update 2026-05-12 / Kim Live 1.5.8: se agrega un modelo persistente de acciones preparadas. Cuando una escritura devuelve `requires_confirmation`, el servidor guarda el `confirm_payload` como `prepared_action_id`; el frontend puede confirmarlo con boton, y Kim tambien puede confirmarlo con `provider=all`, `action=confirm_prepared`.

Update 2026-05-12 / Kim Live 1.5.11: se agrega autorizacion ligera para acciones sensibles. Lectura y busqueda siguen sin friccion; ejecutar `confirm_prepared` o cualquier `confirm=true` requiere una frase de autorizacion o PIN guardado en macOS Keychain. La frase/PIN no se escribe en logs ni en memoria.

Update 2026-05-13 / Kim Live 1.5.12: se agrega el buzon `business@aipeople.io`, se actualiza el PIN en Keychain, y las acciones preparadas confirmadas se eliminan del cache para evitar dobles ejecuciones por clic repetido.

Update 2026-05-13 / Kim Live 1.5.13: el bridge de Hostinger agrega automaticamente la firma acordada de Kim Yan a `draft_email`, `draft_reply`, `send_email` y `reply_email`, salvo que Kim pase `no_signature=true` o una `signature` personalizada.

Update 2026-05-13 / Kim Live 1.5.14: se agrega provider `twilio` para `status`, `list_numbers`, `send_sms` y `send_whatsapp`. Los mensajes se preparan con confirmacion antes de enviarse.

## Regla de seguridad

Kim puede leer estado en vivo sin confirmacion adicional. Para cualquier escritura debe seguir este flujo:

1. Preparar la accion con `confirm=false`.
2. Explicar al doctor que va a cambiar.
3. Esperar confirmacion explicita.
4. Ejecutar la accion con `confirm=true`.
5. Esperar respuesta de la API.
6. Guardar evidencia en memoria y responder si la API confirmo o fallo.

Desde 1.5.11, si el servidor responde `requires_security_phrase=true`, Kim debe pedir al doctor la frase de autorizacion o PIN y volver a confirmar. La autorizacion dura 15 minutos por sesion. No repetir ni guardar la frase en documentos, memorias o tareas.

Desde 1.5.8, Kim debe preferir confirmar asi:

```json
{
  "provider": "all",
  "action": "confirm_prepared",
  "parameters": {
    "prepared_action_id": "ACT-YYYYMMDD-HHMMSS-XXXXXX"
  },
  "confirm": true
}
```

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

Para revisar el estado del candado:

```json
{
  "provider": "all",
  "action": "security_status"
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

Templates 1.5.8:

- `create_task` acepta `title`, `subject`, `task_name` o `task` como `name`.
- `description` acepta `body`, `content`, `message`, `notes`, `summary` o `text`.
- Si falta `list_id`, pero hay `space_name`, el bridge busca `list_name`; si no existe, prepara crear la lista antes de crear la tarea.
- `update_task` y `comment_task` pueden ubicar una tarea por `task_id`, URL o nombre dentro de una lista.

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

Templates 1.5.8:

- `create_page` acepta `subject`, `asunto`, `name` o `page_title` como `title`.
- `content` acepta `body`, `text`, `message`, `description` o `summary`.
- Notion no permite crear una pagina de integracion sin padre real. No usar `root`; se requiere `parent_page_id` o `parent_database_id` compartido con la integracion `KimOne`.

Nota: Codex Desktop ya tiene acceso Notion por MCP, pero ese acceso vive en esta sesion de Codex, no dentro del servidor local de Kim Live. Para que Kim Live opere Notion sola, se necesita token de integracion Notion o un worker remoto con acceso MCP.

## Sonido de operacion

Kim Live usa un tono tipo caja musical mientras interactua con ClickUp/Notion. El tono de investigacion web queda separado como sonido de cuenco.

## Evidencia y memoria

Cada accion del bridge queda registrada en:

```text
BIFROST/MEMORY/context/api_bridge_actions.jsonl
```

Tambien se agrega una nota diaria y un evento en el inbox de Kim Live.

## Accion generica

Kim puede pedir acciones de alto nivel y dejar que el bridge enrute:

- `send_email` -> `hostinger_mail.send_email`
- `reply_email` -> `hostinger_mail.reply_email`
- `send_sms` -> `twilio.send_sms`
- `send_whatsapp` -> `twilio.send_whatsapp`
- `create_task` -> `clickup.create_task`
- `update_task` -> `clickup.update_task`
- `comment_task` -> `clickup.comment_task`
- `create_page` -> `notion.create_page`

Ejemplo:

```json
{
  "provider": "all",
  "action": "send_email",
  "parameters": {
    "to": "cliente@example.com",
    "subject": "Seguimiento",
    "body": "Mensaje completo."
  },
  "confirm": false
}
```

## Twilio

Credenciales en macOS Keychain:

```text
service: codex.twilio.account_sid
service: codex.twilio.auth_token
service: codex.twilio.api_key_sid
service: codex.twilio.api_key_secret
service: codex.twilio.default_from_number
account: dryehoshuapython
```

Acciones:

- `status`: valida credenciales y cuenta.
- `list_numbers`: lista numeros entrantes comprados/asignados y capacidades `voice`, `sms`, `mms`.
- `send_sms`: prepara/envia SMS con `to`, `body` y `from`/`from_number` opcional.
- `send_whatsapp`: prepara/envia WhatsApp usando formato `whatsapp:+numero`; requiere sender/sandbox aprobado en Twilio.

Reglas:

- No comprar numeros desde Kim Live sin confirmacion humana explicita.
- `send_sms` y `send_whatsapp` siempre deben iniciar con `confirm=false`; luego el doctor confirma con `confirm_prepared` o el boton.
- Si Twilio devuelve `401`, el dato pendiente suele ser el Auth Token correcto o un API Key SID que empieza con `SK...`.

## Hostinger multi-buzon

Default desde 2026-05-12: `founder@aipeople.io`.

Buzones activos:

- `founder@aipeople.io`
- `founder@aipeople.work`
- `business@aipeople.io`
- `business@tescaelements.com`
- `ceo@tescaelements.com`

Kim puede seleccionar remitente con `mailbox`, `from`, `account`, `sender`, `selected_mailbox` o `active_mailbox`. Aliases disponibles:

- `founder`, `aipeople`, `ai people`, `aipeople.io`
- `work`, `aipeople.work`
- `business aipeople`, `business ai people`, `aipeople business`, `business io`
- `business`, `tesca business`
- `ceo`, `tesca`, `tesca ceo`

Acciones multi-buzon:

- `list_mailboxes`: lista buzones activos y aliases.
- `switch_mailbox`: cambia/declara el buzon activo. Kim debe conservar `selected_mailbox` en la siguiente lectura, envio o limpieza.

Envio:

- Si falta `subject`, el bridge genera uno por marca: AI People o Tesca Elements.
- `from_name` acepta `sender_name`, `display_name` o `nombre_remitente`; si falta, usa un nombre visible por marca.
- Firma automatica: `Kim Yan` / `Augmented Intelligence Assistant, created by Dr. Yehoshua`.
- Para usar otra firma, pasar `signature`/`firma`; para omitirla, pasar `no_signature=true`.

Acciones de higiene de correo:

- `list_folders`: lista carpetas IMAP.
- `mark_spam`: mueve UID(s) a Junk/Spam.
- `move_to_trash`: mueve UID(s) a Trash/Papelera.
- `archive_message`: mueve UID(s) a Archive si existe.
- `move_message`: mueve UID(s) a una carpeta indicada en `target_folder`.

Todas requieren preparacion y confirmacion. No hay borrado permanente automatico.
