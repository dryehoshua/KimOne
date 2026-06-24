# Kim Diagrams Bridge

Kim Diagrams Bridge permite que Kim edite diagramas de diagrams.net/draw.io conversando con el usuario y aplicando cambios estructurados sobre archivos `.drawio` XML. Codex queda como fallback de desarrollo, no como dependencia operativa diaria.

## Flujo operativo

1. El doctor pide un cambio en lenguaje natural.
2. Kim identifica el archivo `.drawio` y ejecuta `provider=diagrams action=inspect_file`.
3. Kim convierte la instruccion en operaciones estructuradas.
4. Si el cambio modifica el archivo, Kim solicita confirmacion.
5. Kim ejecuta `apply_operations` o `apply_text_replacements`.
6. El bridge guarda backup automatico antes de escribir.
7. Kim ejecuta `layout_analyze` para detectar solapes, tamanos pobres o problemas visuales.
8. Kim genera `preview_svg` para mostrar una vista rapida en Kim Live.
9. Si el doctor quiere revisar en la app, Kim ejecuta `present_file`.

## Acciones soportadas

- `status`: muestra capacidades del puente.
- `inspect_file`: lista etiquetas/celdas de un `.drawio`.
- `layout_analyze`: revisa geometria, solapes, alineacion y riesgos visuales.
- `preview_svg`: genera un SVG simple para vista previa en Kim Live.
- `present_file`: abre el archivo en diagrams.net/draw.io o app predeterminada.
- `close_file`: cierra ventana frontal de draw.io/diagrams.net con confirmacion.
- `queue_edit`: guarda una solicitud cuando la instruccion es demasiado ambigua.
- `apply_text_replacements`: reemplaza textos en nodos.
- `apply_operations`: aplica operaciones estructuradas.

## Operaciones de `apply_operations`

- `update_label`: cambia texto de un nodo por `id` o etiqueta.
- `add_text_node`: agrega una caja nueva con texto.
- `move`: mueve un cuadro por `dx/dy` o `direction=right|left|up|down`.
- `resize`: ajusta ancho/alto o incrementos `dw/dh`.
- `align`: alinea un nodo contra otro por eje `x` o `y`.

Ejemplo:

```json
{
  "path": "/Users/.../diagram.drawio",
  "operations": [
    {"op": "update_label", "target": "Proceso viejo", "text": "Proceso nuevo"},
    {"op": "move", "target": "API Bridge", "direction": "right", "amount": 80},
    {"op": "resize", "target": "Cliente", "dw": 40},
    {"op": "add_text_node", "text": "Validacion", "x": 420, "y": 260}
  ]
}
```

## Reglas visuales

- Mantener un flujo dominante: izquierda a derecha o arriba hacia abajo.
- Evitar mezclar orientaciones salvo por swimlanes o grupos claros.
- Mantener espaciado consistente de 40 a 80 px entre nodos principales.
- Evitar solapes; debe quedar al menos 24 px de aire visual.
- Usar cajas legibles: minimo recomendado 120 x 56 px.
- Si el texto supera 42 caracteres, aumentar ancho o dividir la idea.
- Usar maximo 5 a 7 elementos por grupo visual; dividir si crece.
- En procesos, usar verbos cortos. En entidades, usar nombres claros.
- Priorizar simetria, alineacion por columnas/filas y conectores limpios.

## Formato requerido

El bridge trabaja mejor con `.drawio` guardado como XML no comprimido. Si `inspect_file` devuelve `compressed_diagram_payload=true`, abrir en diagrams.net y guardar/exportar como XML no comprimido antes de edicion fina.

## Seguridad

Toda accion que escribe el archivo guarda backup y requiere confirmacion. Acciones destructivas o de cierre de ventana tambien requieren confirmacion. `preview_svg`, `inspect_file` y `layout_analyze` son de lectura/generacion auxiliar.

## Presentacion

`preview_svg` permite mostrar una vista rapida dentro de Kim Live. `present_file` abre el diagrama real en diagrams.net/draw.io. Si el archivo ya estaba abierto y fue modificado por Python, la app puede requerir recargar/reabrir para reflejar cambios externos.
