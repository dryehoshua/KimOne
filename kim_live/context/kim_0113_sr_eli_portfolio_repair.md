# KIM-0113 Sr Eli Portfolio Repair

Fecha: 2026-06-18

## Fuente de verdad vigente

El override canonico del Portafolio A Sr. Eli queda en `portfolio_report_overrides.json` version `KIM-0113`.

- 12 posiciones ejecutadas/en mercado.
- 11 ordenes pendientes.
- 23 lineas vivas para cliente mas balance cuando se envia reporte completo.
- ONDO/A20 sigue removida.
- ADA/A13 y DOGE/A15 siguen consumidas dentro de sus posiciones consolidadas y no deben revivirse como pendientes separadas.

## Ordenes corregidas

- A14 APTUSDT refuerzo pendiente: 1800 USD @ 0.54. Esta orden se mantiene.
- A25 DOTUSDT refuerzo pendiente: 1800 USD @ 0.72. Esta instruccion fresca reemplaza memoria previa que decia 0.7002.
- A26 FTTUSDT refuerzo pendiente: 1800 USD @ 0.18. Esta instruccion fresca reemplaza memorias antiguas de FTT.

## UI Paper Broker / Portfolio

El panel manual ahora debe permitir:

- Filtrar `Todas`, `Ejecutadas`, `Pendientes` y `Removidas`.
- Agregar orden pendiente desde el panel con orden, simbolo, entrada y monto.
- Editar estado, simbolo, etiqueta, monto, entrada, credito, lado, fuente e ID.
- Copiar linea individual.
- Marcar ejecutada o pendiente desde cada fila.
- Eliminar con confirmacion.
- Preparar aglomeracion desde la pestana de sugerencias; la accion requiere PIN/frase antes de aplicarse.
- Separar una posicion consolidada si conserva `split_members`; la accion requiere PIN/frase.

## Validaciones realizadas

- API `manual_orders`: `KIM-0113`, 12 active, 11 pending, 1 removed.
- Preview WhatsApp completo: 23 lineas cliente + balance, 0 precios bloqueados.
- Ledger warnings: 0 en reporte cliente porque los conflictos viejos quedaron resueltos por override canonico.
- Sugerencias de aglomeracion detectadas: APT, DOT, FTT, LUNC, NEAR y SOL.

## Regla operativa

Kim no debe calcular el reporte del Sr. Eli desde notas libres ni desde drafts viejos del ledger cuando exista override manual canonico. Para reporte cliente, WhatsApp y balance, usar `KIM-0113` como fuente principal, validar precios frescos y bloquear envio si alguna linea no tiene precio aprobado.
