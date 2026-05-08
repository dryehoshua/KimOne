# KIM-0036 - Realtime local repair

## Objetivo

Revisar por que las llamadas Realtime locales de Kim Live dejaron de funcionar y dejar diagnosticos visibles para la prueba humana.

## Diagnostico

- El servidor local estaba activo en `http://127.0.0.1:8765`.
- `/api/status` respondia correctamente.
- `/api/openai-status` confirmaba OpenAI configurado.
- `/api/realtime-token` emitia secretos efimeros validos para `gpt-realtime`.
- La sesion efimera reportaba `output_modalities: ["audio"]`.
- El frontend solicitaba algunas respuestas con `modalities`, y OpenAI Realtime rechazo el evento con `Unknown parameter: response.modalities`.

## Cambios

- Kim Live sube a `v1.4.6`.
- El frontend ya no envia `response.modalities` en ningun `response.create`; deja que la sesion Realtime decida la salida de audio.
- Kim Live cambia de token efimero directo en navegador a la interfaz unificada:
  el browser manda el SDP a `/api/realtime-call` y el servidor local lo reenvia a OpenAI con la API key normal.
- Se agregaron mensajes de diagnostico para:
  - permiso de microfono bloqueado;
  - pagina abierta por IP local sin HTTPS;
  - fallo SDP de OpenAI;
  - desconexion WebRTC;
  - fallo ICE;
  - bloqueo de audio/autoplay en Safari.
- Se agrego `/api/client-log` para guardar en memoria local los eventos de navegador durante el arranque de Realtime.
- La evidencia de cliente confirma que el microfono abre, SDP responde 200, ICE conecta, llega remote track y abre data channel.

## Verificacion

- `python3 -m py_compile server.py`
- JavaScript del HTML validado con `node --check`.
- LaunchAgent reiniciado.
- `GET /api/status` responde `version: 1.4.6`.
- `GET /api/realtime-token` devuelve token efimero, modelo `gpt-realtime`, voz `marin` y modalidad `audio`.
- `POST /api/realtime-call` rechaza SDP invalido con error claro, confirmando que el endpoint local esta activo.

## Prueba pendiente

La prueba final depende del permiso real de microfono en el navegador. Abrir:

`http://127.0.0.1:8765`

Luego recargar, pulsar `Conversar` y aceptar microfono. Si Kim Live se abre por IP LAN, el navegador puede bloquear el microfono salvo que la pagina use HTTPS.
