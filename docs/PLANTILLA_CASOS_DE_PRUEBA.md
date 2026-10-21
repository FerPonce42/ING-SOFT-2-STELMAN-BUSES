# Plantilla de casos de prueba

Una tabla por capa y por persona. Copia este formato, uno por fila de prueba.

**Integrante:** ______  **Módulo:** ______  **Capa:** Dominio / Repositorio / Servicio

| Clase/Método | Caso de prueba | Valores de prueba | Resultado esperado |
|---|---|---|---|
| `validaciones.texto_requerido` | Texto solo con espacios | `"   "`, etiqueta `"La placa"` | Lanza `ReglaNegocioError("La placa es obligatorio.")` |
| `validaciones.texto_requerido` | Texto con espacios alrededor | `"  abc "` | Devuelve `"abc"` |
| `BusService.registrar` | Placa ya registrada | `existe_placa -> True` | Lanza `ReglaNegocioError`; `crear` no se llama |
