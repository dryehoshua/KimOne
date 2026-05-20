# Kim Live API Bridge Spec

Update 2026-05-20 / Kim Live 1.5.32: recepcion Twilio refinada. Si el caller inbound es desconocido, Kim saluda sencillo, se presenta, explica brevemente Ai People y pide primero el nombre. Si el caller ya esta identificado, Kim saluda por nombre y continua el hilo previo/pending propio del contacto, sin revelar informacion de terceros.

Update 2026-05-20 / Kim Live 1.5.31: protocolo Twilio actualizado para ahorrar tiempo y tokens: ante llamadas mudas o fallas de voz, el primer descarte obligatorio es saldo/cuota de OpenAI Realtime (`insufficient_quota`) antes de revisar Twilio, Cloudflare, prompts o frontend. Los reads de Keychain para credenciales bajan de 60s a 8s para evitar que Kim Live quede congelada por una llave opcional.

Update 2026-05-19 / Kim Live 1.5.30: la landing publica de `kim.aipeople.app` queda en ingles con el mensaje "The first capable AI employee" y creditos a Dr. Yehoshua / Ai People. Se agrega avatar digital propio de Kim como figura de particulas en canvas. Twilio Realtime ahora registra errores de OpenAI con detalle seguro y guarda el intento/transcript aunque la API cierre por cuota (`insufficient_quota`) o macOS bloquee escritura en `BIFROST/MEMORY/calls`, usando fallback local en runtime.

Update 2026-05-19 / Kim Live 1.5.29: `kim.aipeople.app` ahora muestra una landing publica de Kim para Ai People con escena visual, propuesta comercial y formularios de login/solicitud de acceso. Las APIs sensibles quedan protegidas por cookie de sesion; el codigo privado se valida desde Keychain (`codex.kim.site_access_code`) con fallback al PIN de seguridad existente. Las solicitudes publicas se guardan como leads en `BIFROST/CRM/leads/kim_site_leads.jsonl`.

Update 2026-05-18 / Kim Live 1.5.28: Twilio inbound ahora crea un contexto `INBOUND-<CallSid>` antes de abrir Realtime. Kim por telefono opera como recepcion/secretaria, identifica el numero entrante contra `person_context_index`, confirma identidad, atiende interesados en Tesca Elements, Ignis o Ai People con informacion general, registra recados y evita revelar pendientes de terceros. El canal Twilio comparte memoria BIFROST con Kim Local, pero se documenta como superficie distinta de la interfaz local/web.

Update 2026-05-18 / Kim Live 1.5.27: `kim_memory_search` ya busca tanto transcripts literales como archivos reales de BIFROST (`knowledge`, `context`, `calls`, `documents`, `person_contexts`, `portfolios`, `CRM` y `docs`) para evitar respuestas sin fuente como `Related files: 0`. Se agrega `BIFROST/MEMORY/context/person_context_index.json`: un indice por persona con contacto, telefonos, context blocks, intentos, transcripts, estado y acciones programadas. ClickUp agrega un mapa operativo en `BIFROST/MEMORY/context/clickup_operation_map.json` para convertir voz del cliente en `team/space/list` sin pedir IDs. Notion deja de bloquear la conversacion si falta `parent_id`: intenta resolver un destino default y, si no hay pagina/base compartida, guarda una nota en `BIFROST/MEMORY/notion_outbox`.

Update 2026-05-17 / Kim Live 1.5.26: se agregan `context blocks` para llamadas externas. Cada llamada preparada conserva un `CTX-*` estable con objetivo, contacto, contexto, intentos, estado, transcript y `workflow_target`, persistido en `BIFROST/MEMORY/context/external_call_context_blocks.json` y `BIFROST/MEMORY/calls/_context_blocks/`.

Update 2026-05-16 / Kim Live 1.5.24: las llamadas Twilio crean memoria `PHONE-<CallSid>.md` desde el intento inicial y actualizan ese mismo registro con callbacks `ringing`, `in-progress`, `completed`, `no-answer`, `busy`, `failed` o `canceled`. `call_report` ya ve intentos sin audio, y `sync_call_attempts` reconcilia callbacks viejos con CRM local y Pipedrive sin iniciar llamadas nuevas.

Update 2026-05-15 / Kim Live 1.5.23: se agrega memoria tipo biblioteca. Kim puede buscar transcripts literales con `kim_memory_search`; la revision bibliotecaria revisa la conversacion guardada, crea tarjetas de conocimiento en `BIFROST/MEMORY/knowledge`, actualiza CRM local cuando hay datos claros y prepara tareas ClickUp detectadas por contexto. Las escrituras externas siguen requiriendo confirmacion.

Update 2026-05-15 / Kim Live 1.5.22: CRM local ya no reemplaza `display_name` por el telefono cuando una actualizacion llega solo con `phone`, conserva `contact_type` si no se envio uno nuevo, reutiliza un contacto existente cuando hay una coincidencia exacta unica por nombre, y limpia fichas Markdown obsoletas del mismo contacto para evitar duplicados como `Isaac Kranz` / `Isaac Krantz`.

Update 2026-05-15 / Kim Live 1.5.21: Kim Live ya guarda el transcript literal por sesion sin duplicar el indice de conversaciones, permite autosave silencioso desde el frontend y agrega `provider=pipedrive action=sync_persons` para bajar contactos de Pipedrive al CRM local de BIFROST como primer paso de la rutina diaria de sincronizacion.

Update 2026-05-15 / Kim Live 1.5.20: Pipedrive phone lookup now uses the local BIFROST CRM contact as a fallback to recover `person_id` and fetch the exact Pipedrive person before fuzzy search. This keeps contacts like Isaac Krantz discoverable by phone after the first sync.

Fecha: 2026-05-08.
Tarea: KIM-0034 / KIM-0035.

## Objetivo

Preparar a Kim Live para leer y modificar informacion viva de ClickUp y Notion desde una conversacion, sin depender solo de snapshots ni de una ejecucion manual posterior de Codex.

Update 2026-05-12 / Kim Live 1.5.8: se agrega un modelo persistente de acciones preparadas. Cuando una escritura devuelve `requires_confirmation`, el servidor guarda el `confirm_payload` como `prepared_action_id`; el frontend puede confirmarlo con boton, y Kim tambien puede confirmarlo con `provider=all`, `action=confirm_prepared`.

Update 2026-05-12 / Kim Live 1.5.11: se agrega autorizacion ligera para acciones sensibles. Lectura y busqueda siguen sin friccion; ejecutar `confirm_prepared` o cualquier `confirm=true` requiere una frase de autorizacion o PIN guardado en macOS Keychain. La frase/PIN no se escribe en logs ni en memoria.

Update 2026-05-13 / Kim Live 1.5.12: se agrega el buzon `business@aipeople.io`, se actualiza el PIN en Keychain, y las acciones preparadas confirmadas se eliminan del cache para evitar dobles ejecuciones por clic repetido.

Update 2026-05-13 / Kim Live 1.5.13: el bridge de Hostinger agrega automaticamente la firma acordada de Kim Yan a `draft_email`, `draft_reply`, `send_email` y `reply_email`, salvo que Kim pase `no_signature=true` o una `signature` personalizada.

Update 2026-05-13 / Kim Live 1.5.14: se agrega provider `twilio` para `status`, `list_numbers`, `send_sms` y `send_whatsapp`. Los mensajes se preparan con confirmacion antes de enviarse.

Update 2026-05-13 / Kim Live 1.5.15: se agregan callbacks `/twilio/status` y `/twilio/sms` para guardar retroalimentacion de llamadas, mensajes y respuestas entrantes.

Update 2026-05-13 / Kim Live 1.5.16: se agrega CRM local en `BIFROST/CRM` con SQLite y exportes Markdown, provider `crm`, llamadas Twilio salientes con confirmacion, y agenda local para `schedule_call` / `schedule_sms`.

Update 2026-05-14 / Kim Live 1.5.17: las llamadas Twilio salientes pueden llevar `call_context`, `objective`, `questions`, `report_to_doctor`, `contact_name` y `relationship`. El contexto se guarda como `twilio_call_contexts.json`, viaja como `kim_context_id` en TwiML Media Streams y se inyecta al prompt Realtime para que Kim no salude como si hablara con el doctor cuando llama a terceros.

Update 2026-05-14 / Kim Live 1.5.18: el puente Twilio Realtime espera el evento `start` antes de configurar OpenAI, de modo que `kim_context_id` llegue antes del primer saludo. Se agregan `latest_call` y `call_report` para que Kim Live lea transcripciones y reporte lo ocurrido en llamadas guardadas.

Update 2026-05-15 / Kim Live 1.5.19: se agrega provider `pipedrive` con token guardado en Keychain. Kim puede buscar/listar personas con coincidencia flexible, crear/actualizar personas, crear deals, actividades y notas. Toda escritura requiere confirmacion y sincroniza contactos relevantes con BIFROST CRM local.

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

## Herramientas Realtime

Kim Live expone `kim_api_bridge`, `kim_memory_search` y `kim_memory_router` al modelo Realtime.

Regla de memoria 1.5.23:

- El transcript literal es la fuente primaria.
- Desde 1.5.27, los archivos BIFROST relevantes tambien son fuente primaria: portafolios, fichas CRM, context blocks, knowledge cards y docs.
- Desde 1.5.27, antes de llamar, escribir o responder sobre una persona, Kim debe buscar por nombre/telefono para cargar `person_contexts/<persona>.md` y los `CTX-*` relacionados.
- Los resumenes son derivados y sirven para orientacion rapida, no como evidencia unica.
- Para responder preguntas de contexto, Kim debe usar `kim_memory_search` antes de sintetizar cuando no tenga el dato fresco en la conversacion activa.
- `kim_memory_router` solo decide el dominio correcto: portafolio, tareas, CRM/clientes, voz remota o memoria general.
- Kim no debe cargar todo BIFROST; debe recuperar snippets relevantes y citar ruta/session_id cuando el contexto importe.

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

## Pipedrive

Kim Live puede usar Pipedrive con API token personal guardado en macOS Keychain:

```text
service: codex.pipedrive.api_token
service: codex.pipedrive.company_domain
account: dryehoshuapython
```

Provider `pipedrive`:

- `status`: valida token, usuario y empresa.
- `search_persons` / `list_persons`: busca contactos con coincidencia flexible por nombre, email o telefono.
- `sync_persons`: trae personas desde Pipedrive y hace upsert en `BIFROST/CRM` sin escribir en Pipedrive.
- `get_person`: lee una persona por `person_id` o busqueda unica.
- `upsert_person`: crea o actualiza persona. Requiere confirmacion y sincroniza BIFROST CRM.
- `list_deals` / `search_deals`: consulta oportunidades.
- `create_deal`: crea oportunidad. Requiere confirmacion.
- `update_deal`: actualiza oportunidad por `deal_id`. Requiere confirmacion.
- `create_activity`: crea actividad comercial, llamada, reunion o seguimiento. Requiere confirmacion.
- `create_note`: crea nota ligada a persona, organizacion o deal. Requiere confirmacion.

Regla: Kim no debe decir que no existe un contacto sin usar `search_persons` y revisar candidatos cercanos por `match_score`.

## Sonido de operacion

Kim Live usa un tono tipo caja musical mientras interactua con ClickUp/Notion. El tono de investigacion web queda separado como sonido de cuenco.

## Evidencia y memoria

Cada accion del bridge queda registrada en:

```text
BIFROST/MEMORY/context/api_bridge_actions.jsonl
```

Tambien se agrega una nota diaria y un evento en el inbox de Kim Live.

Las conversaciones de Kim Live se guardan por `session_id` en `BIFROST/MEMORY/calls/YYYY-MM-DD/` y el autosave silencioso actualiza el mismo archivo en lugar de crear duplicados.

Desde 1.5.23, la revision bibliotecaria usa el transcript guardado para decidir automaticamente:

- `knowledge_cards`: se guardan como Markdown en `BIFROST/MEMORY/knowledge/<dominio>/`.
- `crm_updates`: si hay nombre y telefono/correo con confianza alta, actualiza `BIFROST/CRM` local.
- `clickup_tasks`: se preparan como accion ClickUp con `prepared_action_id`; el doctor confirma desde el boton o con `confirm_prepared`.
- No se ejecutan escrituras externas sin confirmacion explicita.

## Accion generica

Kim puede pedir acciones de alto nivel y dejar que el bridge enrute:

- `send_email` -> `hostinger_mail.send_email`
- `reply_email` -> `hostinger_mail.reply_email`
- `send_sms` -> `twilio.send_sms`
- `send_whatsapp` -> `twilio.send_whatsapp`
- `call_phone` -> `twilio.call_phone`
- `schedule_call` -> `twilio.schedule_call`
- `schedule_sms` -> `twilio.schedule_sms`
- `save_contact` -> `crm.upsert_contact`
- `pipedrive_upsert_person` -> `pipedrive.upsert_person`
- `pipedrive_create_deal` -> `pipedrive.create_deal`
- `pipedrive_create_activity` -> `pipedrive.create_activity`
- `pipedrive_create_note` -> `pipedrive.create_note`

## CRM Local

La base estructurada vive en:

- `BIFROST/CRM/crm.sqlite`
- `BIFROST/CRM/contacts/by_type/<tipo>/<contacto>.md`
- `BIFROST/CRM/companies/`
- `BIFROST/CRM/interactions/`
- `BIFROST/CRM/schedules/`

Provider `crm`:

- `status`: revisa conteos y ruta de la base.
- `list_contacts`: busca por nombre, telefono, correo, empresa o tipo.
- `upsert_contact`: crea o actualiza un contacto. Requiere confirmacion.
- `record_note`: registra una nota interna. Requiere confirmacion.

Provider `twilio`:

- `call_phone`: inicia llamada saliente con el webhook de Kim Live.
- `schedule_call`: guarda llamada programada; el scheduler local la ejecuta al vencer.
- `schedule_sms`: guarda SMS programado; el scheduler local lo ejecuta al vencer.

Para llamadas a terceros, `call_phone` debe incluir:

```json
{
  "to": "+5255...",
  "contact_name": "Nombre de la persona",
  "relationship": "cliente, familiar, prospecto, proveedor...",
  "call_context": "Contexto que Kim debe saber pero no leer literalmente.",
  "objective": "Objetivo concreto de la llamada.",
  "questions": ["Pregunta 1", "Pregunta 2"],
  "report_to_doctor": "Datos que Kim debe traer de regreso."
}
```

Las llamadas y SMS quedan enlazados a CRM como interacciones. Las llamadas Realtime tambien guardan transcript en `BIFROST/MEMORY/calls`. Desde 1.5.24, los intentos no contestados tambien guardan un archivo `PHONE-<CallSid>.md` con historial de estados y ruta a CRM/Pipedrive.

Desde 1.5.26, cada llamada externa queda ademas enlazada a un `context_block_id`. Ese bloque permite retomar el hilo sin que el doctor repita el contexto: objetivo, preguntas, persona, respuestas, intentos y siguiente paso viven bajo el mismo `CTX-*`.

Provider `clickup` 1.5.27:

- Kim no debe pedir `list_id` ni `space_id` para tareas normales.
- El bridge intenta mapear el texto a una lista existente con `clickup_operation_map.json`.
- Si el texto menciona un cliente/lista existente, se usa esa lista.
- Si habla de portafolio/Ignis/Eli, se enruta a `Ignis Stock Financials / Investor follow-up / Khalil`.
- Si habla de producto Kim/BIFROST/API/Twilio/Telegram, se enruta al fallback operativo disponible hasta que exista un Space de producto dedicado.
- Si habla de cliente/prospecto/CRM/Isaac, se enruta a `Ai people / Client Follow-up`.

Provider `notion` 1.5.27:

- Si falta un parent real, Kim no debe pedir IDs repetidamente.
- El bridge intenta usar `BIFROST/MEMORY/context/notion_default_parent.json`.
- Si no hay destino compartido/configurado, guarda la nota en `BIFROST/MEMORY/notion_outbox` para no perder el contenido y reporta que falta configurar el parent de Notion.
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
- `call_phone`: prepara/ejecuta llamada con contexto estructurado; al confirmar crea memoria del intento desde `queued`.
- `latest_call`: lee la ultima llamada o intento guardado.
- `call_report`: lee transcripciones e intentos por `call_sid`, `context_id`, `phone`, `contact_name` o `limit`.
- `sync_call_attempts`: reconcilia callbacks Twilio ya recibidos y crea/actualiza memoria, CRM y actividad Pipedrive. No llama a nadie.

Reglas:

- No comprar numeros desde Kim Live sin confirmacion humana explicita.
- `send_sms` y `send_whatsapp` siempre deben iniciar con `confirm=false`; luego el doctor confirma con `confirm_prepared` o el boton.
- Si una llamada no se concreta, Kim debe reportar el estado real (`no-answer`, `busy`, `failed`, etc.) desde `call_report`, no decir que no hay registro.
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
