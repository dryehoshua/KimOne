# KIM-0035 - TradingView Market Desk

Fecha: 2026-05-07.

## Objetivo

Agregar TradingView a Kim Live para que el doctor pueda revisar graficos de mercado durante la conversacion y mandar el contexto del grafico a Kim.

## Integracion elegida hoy

Se usa el widget oficial Advanced Chart de TradingView.

No requiere API key para comenzar.

Links:

- Advanced Chart Widget: https://www.tradingview.com/widget-docs/widgets/charts/advanced-chart/
- Widget docs: https://www.tradingview.com/widget-docs/
- Webhook alerts: https://www.tradingview.com/support/solutions/43000529348/
- Charting Library / datafeed: https://www.tradingview.com/charting-library-docs/latest/connecting_data/datafeed-api/

## Limites importantes

- El widget de TradingView corre dentro de un iframe/script externo.
- Kim Live puede mostrar el grafico, pero no debe intentar scrapear datos internos de TradingView.
- Para que Kim lea velas visualmente, el doctor debe adjuntar una captura del grafico o dictar observaciones.
- Para precios/indicadores estructurados se necesitara una fuente de datos posterior.
- Para alertas automaticas se usaran webhooks de TradingView cuando Kim Live tenga endpoint HTTPS publico.

## Cambios en Kim Live

- Se agrego un panel `TradingView Market Desk` en la pantalla principal.
- Campo de simbolo TradingView, por ejemplo:
  - `BINANCE:BTCUSDT`
  - `NASDAQ:NVDA`
  - `OANDA:XAUUSD`
  - `FX:EURUSD`
- Selector de temporalidad:
  - 15m
  - 1h
  - 4h
  - 1D
  - 1W
- Boton `Cargar` para actualizar grafico.
- Boton `Mandar a Kim` para agregar al transcript una solicitud de analisis del simbolo/temporalidad activos.

## Flujo recomendado

1. Abrir Kim Live.
2. Cargar simbolo TradingView.
3. Revisar grafico.
4. Presionar `Mandar a Kim`.
5. Si se necesita analisis visual real, adjuntar captura del grafico.
6. Kim analiza con el playbook del doctor y guarda la tesis en memoria.

## Siguiente fase

- Crear playbook de lectura tecnica del doctor.
- Agregar endpoint para guardar tesis de mercado.
- Agregar webhooks de TradingView para alertas.
- Agregar proveedor de datos para OHLCV/precio estructurado.
