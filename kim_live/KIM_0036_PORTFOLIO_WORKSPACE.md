# KIM-0036 Portfolio Workspace

Fecha: 2026-05-08.

## Decision

El portafolio del Sr. Eli se va a guardar localmente en BIFROST, sin depender de Notion ni ClickUp.

Motivo: durante la prueba, Notion y ClickUp pidieron parametros o ubicaciones que hicieron lenta la operacion. Para no perder contexto ni arriesgar registros financieros, BIFROST queda como fuente primaria local. Notion/ClickUp podran ser espejos o tareas despues.

## Estructura

Jerarquia logica:

```text
Ignis Stock Financials
Clientes
Manejo de Portafolios
Sr. Eli 2026
```

Ruta en disco:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/portfolios/ignis_stock_financials/clientes/manejo_de_portafolios/sr_eli_2026
```

Base central:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/portfolios/portfolio_ledger.sqlite
```

Herramienta:

```text
/Users/dryehoshuapython/Documents/BIFROST/kimtools/portfolios/portfolio_db.py
```

Runtime Kim Live:

```text
/Users/dryehoshuapython/.kim_live/MEMORY/portfolios
```

Kim Live `v1.4.9` puede leer/escribir el portafolio desde su runtime local. Codex creo tambien la base principal en BIFROST. macOS bloqueo la escritura directa del servicio Kim Live sobre algunos archivos ya existentes bajo `Documents/BIFROST/MEMORY/portfolios`; por eso Kim Live usa runtime mirror y Codex puede consolidar/sincronizar a BIFROST cuando haga falta.

## Tablas

- `clients`: clientes.
- `portfolios`: portafolios por cliente.
- `instruments`: instrumentos/monedas.
- `watchlist`: universo de seguimiento del portafolio.
- `positions`: posiciones actuales.
- `transactions`: compras, ventas, transferencias y ajustes.
- `market_consultations`: preguntas, snapshots, analisis y decisiones preliminares.
- `final_changes`: cambios finales confirmados por el doctor.
- `portfolio_snapshots`: valuaciones o estados del portafolio.
- `documents`: rutas a reportes/estados de cuenta/archivos.
- `audit_events`: bitacora tecnica.

## Regla de seguridad

Kim no debe convertir cada conversacion en transaccion final. El flujo correcto es:

1. Guardar consulta o escenario como `market_consultation`.
2. Esperar una frase explicita del doctor como "cambio final", "operacion final", "compra final", "venta final", "ejecutado" o equivalente.
3. Registrar `final_change`.
4. Si ya hay cantidades/precios/fecha, registrar `transaction` con `status=final`; si falta algo, usar `draft`.

## Datos semilla

Universo inicial conversado:

```text
LUNC, DOGE, FTT, AVAX, XLM, HBAR, ONDO, XRP, TRX, ADA/Cardano, SHIB, ZEC, ICP, DOT, WLD, APT, PEPE
```

Referencias previas que requieren confirmacion antes de convertirse en operaciones:

- DOGE: inversion inicial conversada de 2554 USD.
- FTT: inversion inicial conversada de 2000 USD.
- LUNC: inversion inicial conversada de 1000 USD.
- Objetivo conversado: evaluar un portafolio aproximado de 1800 USD.

## Grok API

Se verifico con fuente oficial que xAI si ofrece API. La pagina oficial de xAI API lista `grok-4.3` como disponible por API, capacidades de razonamiento/vision/voice/tool calling/search, y precios por millon de tokens.

Fuente: https://x.ai/api

Esto queda como dato de investigacion; no se integro Grok en KIM-0036.
