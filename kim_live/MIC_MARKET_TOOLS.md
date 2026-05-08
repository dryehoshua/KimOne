# KIM-0037 - Microfono y herramientas de mercado

## Problema

Dr. Yehoshua reporto dos fallas de producto en Kim Live:

- Kim ya respondia por voz, pero no parecia escuchar correctamente por microfono.
- La grafica de TradingView ocupaba espacio en el chat y no le daba a Kim datos reales para analizar.

## Diagnostico

- Los client logs mostraban que Chrome abria `IdeaShare 2ch (Virtual)` como microfono.
- Realtime si estaba conectando, pero el dispositivo de entrada podia no ser el microfono fisico correcto.
- El widget de TradingView es util visualmente, pero Kim no puede leer el iframe directamente.

## Cambios

- Kim Live sube a `v1.4.7`.
- Se agrego selector de microfono en la barra lateral.
- Se agrego prueba de nivel de microfono con medidor visual.
- Realtime usa el `deviceId` elegido por el doctor.
- Si el microfono activo parece virtual, Kim Live advierte cambiar a microfono fisico.
- La grafica pasa a una pestana `Mercados`; el chat recupera su espacio original.
- Se agrego `/api/market-snapshot`.
- Se agrego herramienta Realtime `kim_market_snapshot`.
- El boton `Analizar con Kim` obtiene OHLCV de Binance para simbolos `BINANCE:*` y calcula cierre, EMA20, EMA50, RSI14, soportes, resistencias, cambio y volumen relativo.
- Se corrigieron instrucciones de Kim: no debe decir que ve camara, pantalla o iframe si no recibio imagen o datos.

## Verificacion

- `python3 -m py_compile server.py`
- JavaScript validado con `node --check`.
- `GET /api/status` devuelve `version: 1.4.7`.
- `POST /api/market-snapshot` devuelve snapshot para `BINANCE:BTCUSDT` en `D`.
