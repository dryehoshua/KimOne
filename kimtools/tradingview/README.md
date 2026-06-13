# TradingView Bridge For Kim

Objetivo: conectar alertas de TradingView con Kim Paper Broker sin depender de crear una alerta manual por cada orden.

## Estrategia Actual

TradingView no ofrece una API publica estable para crear alertas desde backend. El bridge genera un unico Pine Script que vigila todas las ordenes pendientes del Sr. Eli con `request.security()` y dispara `alert()` hacia:

`https://kim.aipeople.app/api/tradingview/webhook`

En TradingView solo debe existir una alerta:

`Kim Sr Eli Paper Broker Alerts / Any alert() function call`

## Comando

```bash
python3 /Users/dryehoshuapython/Documents/BIFROST/kimtools/tradingview/tradingview_alert_bridge.py generate
```

Salidas:

- `kim_sr_eli_paper_alerts_latest.pine`: Pine Script con token real local.
- `kim_sr_eli_paper_alerts_redacted.pine`: copia sin token para revisar/compartir.
- `kim_sr_eli_paper_alerts_manifest.json`: ordenes incluidas e instrucciones.

## Siguiente Paso De Automatizacion

La automatizacion total requiere una sesion TradingView abierta. La ruta recomendada es:

1. El doctor abre TradingView y deja la cuenta logueada.
2. Kim genera el Pine Script.
3. Un runner de UI automation pega/actualiza el script y crea la alerta unica.

Hasta que ese runner este estable, el watcher local de Kim Paper Broker sigue como respaldo.
