-- Datos mínimos para poder usar la app en desarrollo.
-- El dump original trae un hash falso y ninguna ruta asignada al supervisor,
-- así que sin esto nadie podría entrar ni vería datos en el panel.
-- Usuario: aperez_sup   Contraseña: stelman123   (SOLO DESARROLLO)

UPDATE cuenta_usuario SET password_hash = 'scrypt:32768:8:1$Ab0170DbbsCrIVbr$e10f439d8c8e783ff054f59b3e71b807a067b01bc23c89e19488c7cee8d09b15aed7c5905ccb23fe72ccf5bcc82c66a2d4594dc00f65d560c9c383aa8b1f5be3' WHERE nombre_usuario = 'aperez_sup';

INSERT IGNORE INTO supervisor_ruta (fecha_asignacion, id_empleado, id_ruta, fecha_fin, observaciones)
VALUES ('2026-09-01 05:00:00', 2, 1, NULL, 'Asignación inicial (seed de desarrollo)');
