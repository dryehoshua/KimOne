# KIM-0115 Sr Eli Portfolio Command Guard

Fecha: 2026-06-22

## Problema

Kim Live podia tener el portafolio correcto en `portfolio_report_overrides.json`, pero despues caer en rutas viejas o responder por WhatsApp con interpretacion libre. Eso producia errores al pedir rangos, lineas especificas o el portafolio completo.

## Cambios

- `doctor_command` traduce instrucciones como `manda portafolio completo`, `manda A13-A23`, `manda pendientes` y `preflight` a acciones estructuradas de portfolio.
- WhatsApp inbound del Dr. Yehoshua ejecuta el comando de portfolio antes de pasar por el modelo general.
- Lineas sueltas tipo `A14... USDT...` se guardan como referencia; no modifican la fuente canonica ni disparan calculos conversacionales.
- Los reportes calientan precios de todos los simbolos del override manual, no solo del ledger viejo.
- `send_whatsapp_report` guarda el estandar despues del preflight validado.
- El estandar se sincroniza a rutas nuevas y legacy:
  - `MEMORY/IGNIS_FINANCIALS/portfolios/.../sr_eli_2026/portfolio_a_standard.json`
  - `.kim_live/MEMORY/IGNIS_FINANCIALS/portfolios/sr_eli_2026/portfolio_a_standard.json`
  - `MEMORY/portfolios/sr_eli_2026/portfolio_a_standard.json`
  - `.kim_live/MEMORY/portfolios/sr_eli_2026/portfolio_a_standard.json`
  - `MEMORY/portfolios/ignis_stock_financials/.../sr_eli_2026/portfolio_a_standard.json`
- El panel agrega un campo de comando estructurado para preview o ejecucion.

## Estado Validado

- Version: `KIM-0115`.
- Manual entries: 23.
- En mercado: 14.
- Pendientes: 9.
- Vista WhatsApp completa: 23 lineas + balance.
- Preflight `A13-A23`: 11 mensajes, 0 bloqueos.

## Regla

Para Sr. Eli, Kim no debe reconstruir el portafolio desde notas libres ni drafts antiguos. Debe usar `doctor_command`, `client_report`, `whatsapp_preview` o `send_whatsapp_report` sobre el override canonico.
