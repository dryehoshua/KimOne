# KIM-0036 - Realtime local repair

## Objetivo

Revisar por que las llamadas Realtime locales de Kim Live dejaron de funcionar y dejar diagnosticos visibles para la prueba humana.

## Diagnostico

- El servidor local estaba activo en `http://127.0.0.1:8765`.
- `/api/status` respondia correctamente.
- `/api/openai-status` confirmaba OpenAI configurado.
- `/api/realtime-token` emitia secretos efimeros validos para `gpt-realtime`.
- La sesion efimera reportaba `output_modalities: ["audio"]`.
- El frontend solicitaba algunas respuestas con `modalities: ["audio", "text"]`, lo que podia provocar errores de Realtime al iniciar o contestar herramientas.

## Cambios

- Kim Live sube a `v1.4.4`.
- El frontend ahora crea respuestas Realtime solo con modalidad `audio`.
- Se agregaron mensajes de diagnostico para:
  - permiso de microfono bloqueado;
  - pagina abierta por IP local sin HTTPS;
  - fallo SDP de OpenAI;
  - desconexion WebRTC;
  - fallo ICE;
  - bloqueo de audio/autoplay en Safari.
- Se evita gastar token Realtime antes de comprobar que el microfono local abre.

## Verificacion

- `python3 -m py_compile server.py`
- JavaScript del HTML validado con `node --check`.
- LaunchAgent reiniciado.
- `GET /api/status` responde `version: 1.4.4`.
- `GET /api/realtime-token` devuelve token efimero, modelo `gpt-realtime`, voz `marin` y modalidad `audio`.

## Prueba pendiente

La prueba final depende del permiso real de microfono en el navegador. Abrir:

`http://127.0.0.1:8765`

Luego recargar, pulsar `Conversar` y aceptar microfono. Si Kim Live se abre por IP LAN, el navegador puede bloquear el microfono salvo que la pagina use HTTPS.
