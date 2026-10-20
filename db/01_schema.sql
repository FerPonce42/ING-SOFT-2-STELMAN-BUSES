-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 06-09-2026 a las 22:02:32
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `buses`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `almacen`
--

CREATE TABLE `almacen` (
  `id_almacen` int(11) NOT NULL,
  `nombre_sede` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `capacidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `almacen`
--

INSERT INTO `almacen` (`id_almacen`, `nombre_sede`, `direccion`, `capacidad`) VALUES
(1, 'Terminal Norte', 'Av. Las Industrias 100', 50),
(2, 'Patio Sur', 'Carretera Sur Km 15', 120);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asignacion_bus`
--

CREATE TABLE `asignacion_bus` (
  `id_asignacion_bus` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `turno` varchar(50) DEFAULT NULL,
  `observacion` varchar(255) DEFAULT NULL,
  `id_empleado` int(11) NOT NULL,
  `id_bus` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `asignacion_bus`
--

INSERT INTO `asignacion_bus` (`id_asignacion_bus`, `fecha`, `turno`, `observacion`, `id_empleado`, `id_bus`) VALUES
(1, '2026-09-06 06:00:00', 'Mañana', 'Nivel de combustible al 100%', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bus`
--

CREATE TABLE `bus` (
  `id_bus` int(11) NOT NULL,
  `placa` varchar(20) NOT NULL,
  `año_fabricacion` smallint(6) NOT NULL,
  `id_modelo_bus` int(11) NOT NULL,
  `id_almacen` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `bus`
--

INSERT INTO `bus` (`id_bus`, `placa`, `año_fabricacion`, `id_modelo_bus`, `id_almacen`) VALUES
(1, 'ABC-1234', 2024, 1, 1),
(2, 'XYZ-9876', 2025, 2, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bus_ruta`
--

CREATE TABLE `bus_ruta` (
  `id_bus_ruta` int(11) NOT NULL,
  `fecha_asignacion` datetime NOT NULL,
  `fecha_desasignacion` datetime DEFAULT NULL,
  `id_bus` int(11) NOT NULL,
  `id_ruta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `bus_ruta`
--

INSERT INTO `bus_ruta` (`id_bus_ruta`, `fecha_asignacion`, `fecha_desasignacion`, `id_bus`, `id_ruta`) VALUES
(1, '2026-09-01 05:00:00', NULL, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `caja`
--

CREATE TABLE `caja` (
  `id_caja` bigint(20) NOT NULL,
  `fecha` datetime NOT NULL,
  `monto_recaudado` decimal(10,2) NOT NULL,
  `observacion` varchar(255) DEFAULT NULL,
  `id_empleado` int(11) NOT NULL,
  `id_bus` int(11) NOT NULL,
  `id_ruta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `caja`
--

INSERT INTO `caja` (`id_caja`, `fecha`, `monto_recaudado`, `observacion`, `id_empleado`, `id_bus`, `id_ruta`) VALUES
(1, '2026-09-06 14:15:00', 350.50, 'Sin novedades', 1, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `chofer`
--

CREATE TABLE `chofer` (
  `id_empleado` int(11) NOT NULL,
  `nro_licencia` varchar(50) NOT NULL,
  `fecha_primera_licencia` date NOT NULL,
  `id_tipo_licencia` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `chofer`
--

INSERT INTO `chofer` (`id_empleado`, `nro_licencia`, `fecha_primera_licencia`, `id_tipo_licencia`) VALUES
(1, 'LIC-555-XYZ', '2010-05-20', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cuenta_usuario`
--

CREATE TABLE `cuenta_usuario` (
  `id_cuenta` int(11) NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `estado_cuenta` tinyint(1) NOT NULL DEFAULT 1,
  `id_empleado` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cuenta_usuario`
--

INSERT INTO `cuenta_usuario` (`id_cuenta`, `nombre_usuario`, `password_hash`, `estado_cuenta`, `id_empleado`) VALUES
(1, 'aperez_sup', 'hash_falso_827364_xkcd', 1, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleado`
--

CREATE TABLE `empleado` (
  `id_empleado` int(11) NOT NULL,
  `nro_identificacion` varchar(50) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `correo_electronico` varchar(150) DEFAULT NULL,
  `sueldo` decimal(10,2) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_ingreso` date NOT NULL,
  `tipo` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleado`
--

INSERT INTO `empleado` (`id_empleado`, `nro_identificacion`, `nombre`, `apellido`, `fecha_nacimiento`, `correo_electronico`, `sueldo`, `telefono`, `fecha_ingreso`, `tipo`) VALUES
(1, 'ID-888888', 'Carlos', 'Gomez', '1985-04-12', 'cgomez@empresa.com', 1500.00, '+51987654321', '2025-01-15', 'Chofer'),
(2, 'ID-999999', 'Ana', 'Perez', '1990-08-22', 'aperez@empresa.com', 2000.00, '+51987123456', '2024-10-01', 'Supervisor');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleado_horario`
--

CREATE TABLE `empleado_horario` (
  `id_empleado` int(11) NOT NULL,
  `id_horario` int(11) NOT NULL,
  `fecha_efectiva` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleado_horario`
--

INSERT INTO `empleado_horario` (`id_empleado`, `id_horario`, `fecha_efectiva`) VALUES
(1, 1, '2026-09-07');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `horario`
--

CREATE TABLE `horario` (
  `id_horario` int(11) NOT NULL,
  `dia_semana` varchar(20) NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `horario`
--

INSERT INTO `horario` (`id_horario`, `dia_semana`, `hora_inicio`, `hora_fin`) VALUES
(1, 'Lunes', '06:00:00', '14:00:00'),
(2, 'Lunes', '14:00:00', '22:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidencia`
--

CREATE TABLE `incidencia` (
  `id_incidencia` bigint(20) NOT NULL,
  `fecha` datetime NOT NULL,
  `descripcion` varchar(500) NOT NULL,
  `estado` varchar(50) NOT NULL,
  `id_ruta` int(11) DEFAULT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `id_bus` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `incidencia`
--

INSERT INTO `incidencia` (`id_incidencia`, `fecha`, `descripcion`, `estado`, `id_ruta`, `id_empleado`, `id_bus`) VALUES
(1, '2026-09-06 08:30:00', 'Choque leve con vehiculo particular', 'En revision', 1, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidencia_disciplinaria`
--

CREATE TABLE `incidencia_disciplinaria` (
  `id_incidencia` bigint(20) NOT NULL,
  `sancion` varchar(255) NOT NULL,
  `id_tipo_disciplinaria` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidencia_operativa`
--

CREATE TABLE `incidencia_operativa` (
  `id_incidencia` bigint(20) NOT NULL,
  `gravedad` varchar(50) NOT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  `requiere_seguro` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `incidencia_operativa`
--

INSERT INTO `incidencia_operativa` (`id_incidencia`, `gravedad`, `costo`, `requiere_seguro`) VALUES
(1, 'Leve', NULL, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mantenimiento`
--

CREATE TABLE `mantenimiento` (
  `id_mantenimiento` bigint(20) NOT NULL,
  `fecha` datetime NOT NULL,
  `costo_estimado` decimal(10,2) DEFAULT NULL,
  `costo_real` decimal(10,2) DEFAULT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  `id_bus` int(11) NOT NULL,
  `id_proveedor` int(11) NOT NULL,
  `id_tipo_mantenimiento` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mantenimiento`
--

INSERT INTO `mantenimiento` (`id_mantenimiento`, `fecha`, `costo_estimado`, `costo_real`, `descripcion`, `id_bus`, `id_proveedor`, `id_tipo_mantenimiento`) VALUES
(1, '2026-09-06 10:00:00', 500.00, NULL, NULL, 2, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `marca_bus`
--

CREATE TABLE `marca_bus` (
  `id_marca_bus` smallint(6) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `marca_bus`
--

INSERT INTO `marca_bus` (`id_marca_bus`, `nombre`) VALUES
(2, 'Mercedes-Benz'),
(1, 'Volvo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modelo_bus`
--

CREATE TABLE `modelo_bus` (
  `id_modelo_bus` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `id_marca_bus` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `modelo_bus`
--

INSERT INTO `modelo_bus` (`id_modelo_bus`, `nombre`, `id_marca_bus`) VALUES
(1, 'B9R Articulado', 1),
(2, 'O500U Padron', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paradero`
--

CREATE TABLE `paradero` (
  `id_paradero` int(11) NOT NULL,
  `nombre_paradero` varchar(150) NOT NULL,
  `latitud` decimal(10,8) NOT NULL,
  `longitud` decimal(10,8) NOT NULL,
  `direccion_referencia` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `paradero`
--

INSERT INTO `paradero` (`id_paradero`, `nombre_paradero`, `latitud`, `longitud`, `direccion_referencia`) VALUES
(1, 'Estacion Central', -16.40904000, -71.53745000, 'Frente a la plaza principal'),
(2, 'Intercambio Vial Norte', -16.39881000, -71.53692000, 'Cruce de avenidas principales');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedor`
--

CREATE TABLE `proveedor` (
  `id_proveedor` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `contacto` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proveedor`
--

INSERT INTO `proveedor` (`id_proveedor`, `nombre`, `contacto`) VALUES
(1, 'Taller Motors S.A.', 'contacto@motors.com');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recorrido`
--

CREATE TABLE `recorrido` (
  `id_recorrido` int(11) NOT NULL,
  `orden_paradero` int(11) NOT NULL,
  `id_ruta` int(11) NOT NULL,
  `id_paradero` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `recorrido`
--

INSERT INTO `recorrido` (`id_recorrido`, `orden_paradero`, `id_ruta`, `id_paradero`) VALUES
(1, 1, 1, 1),
(2, 2, 1, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ruta`
--

CREATE TABLE `ruta` (
  `id_ruta` int(11) NOT NULL,
  `codigo_ruta` varchar(20) NOT NULL,
  `distancia` decimal(10,2) NOT NULL,
  `duracion_estimada` int(11) NOT NULL,
  `color` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ruta`
--

INSERT INTO `ruta` (`id_ruta`, `codigo_ruta`, `distancia`, `duracion_estimada`, `color`) VALUES
(1, 'EX-101', 25.50, 90, '#FF0000'),
(2, 'B-Line', 15.00, 45, '#0000FF');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `supervisor`
--

CREATE TABLE `supervisor` (
  `id_empleado` int(11) NOT NULL,
  `id_tipo_supervisor` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `supervisor`
--

INSERT INTO `supervisor` (`id_empleado`, `id_tipo_supervisor`) VALUES
(2, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `supervisor_ruta`
--

CREATE TABLE `supervisor_ruta` (
  `fecha_asignacion` datetime NOT NULL,
  `id_empleado` int(11) NOT NULL,
  `id_ruta` int(11) NOT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `observaciones` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_disciplinaria`
--

CREATE TABLE `tipo_disciplinaria` (
  `id_tipo_disciplinaria` smallint(6) NOT NULL,
  `nombre_falta` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_disciplinaria`
--

INSERT INTO `tipo_disciplinaria` (`id_tipo_disciplinaria`, `nombre_falta`, `descripcion`) VALUES
(1, 'Abandono de ruta', 'Desvio no autorizado del recorrido establecido'),
(2, 'Impuntualidad grave', 'Retraso mayor a 15 minutos en el inicio del turno');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_licencia`
--

CREATE TABLE `tipo_licencia` (
  `id_tipo_licencia` smallint(6) NOT NULL,
  `categoria` varchar(10) NOT NULL,
  `pais_emision` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_licencia`
--

INSERT INTO `tipo_licencia` (`id_tipo_licencia`, `categoria`, `pais_emision`, `descripcion`) VALUES
(1, 'AIII', 'Peru', 'Transporte publico masivo y articulado'),
(2, 'AII', 'Peru', 'Transporte publico ligero (minibuses)');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_mantenimiento`
--

CREATE TABLE `tipo_mantenimiento` (
  `id_tipo_mantenimiento` smallint(6) NOT NULL,
  `nombre_servicio` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_mantenimiento`
--

INSERT INTO `tipo_mantenimiento` (`id_tipo_mantenimiento`, `nombre_servicio`) VALUES
(1, 'Preventivo'),
(2, 'Correctivo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_supervisor`
--

CREATE TABLE `tipo_supervisor` (
  `id_tipo_supervisor` smallint(6) NOT NULL,
  `nombre_cargo` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_supervisor`
--

INSERT INTO `tipo_supervisor` (`id_tipo_supervisor`, `nombre_cargo`, `descripcion`) VALUES
(1, 'Jefe de Flota', 'Supervisa el estado general de los vehiculos en terminal'),
(2, 'Controlador de Ruta', 'Monitorea tiempos y frecuencias en paraderos');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `almacen`
--
ALTER TABLE `almacen`
  ADD PRIMARY KEY (`id_almacen`),
  ADD UNIQUE KEY `nombre_sede` (`nombre_sede`);

--
-- Indices de la tabla `asignacion_bus`
--
ALTER TABLE `asignacion_bus`
  ADD PRIMARY KEY (`id_asignacion_bus`),
  ADD KEY `id_empleado` (`id_empleado`),
  ADD KEY `id_bus` (`id_bus`);

--
-- Indices de la tabla `bus`
--
ALTER TABLE `bus`
  ADD PRIMARY KEY (`id_bus`),
  ADD UNIQUE KEY `placa` (`placa`),
  ADD KEY `id_modelo_bus` (`id_modelo_bus`),
  ADD KEY `id_almacen` (`id_almacen`);

--
-- Indices de la tabla `bus_ruta`
--
ALTER TABLE `bus_ruta`
  ADD PRIMARY KEY (`id_bus_ruta`),
  ADD KEY `id_bus` (`id_bus`),
  ADD KEY `id_ruta` (`id_ruta`);

--
-- Indices de la tabla `caja`
--
ALTER TABLE `caja`
  ADD PRIMARY KEY (`id_caja`),
  ADD KEY `id_empleado` (`id_empleado`),
  ADD KEY `id_bus` (`id_bus`),
  ADD KEY `id_ruta` (`id_ruta`);

--
-- Indices de la tabla `chofer`
--
ALTER TABLE `chofer`
  ADD PRIMARY KEY (`id_empleado`),
  ADD UNIQUE KEY `nro_licencia` (`nro_licencia`),
  ADD KEY `id_tipo_licencia` (`id_tipo_licencia`);

--
-- Indices de la tabla `cuenta_usuario`
--
ALTER TABLE `cuenta_usuario`
  ADD PRIMARY KEY (`id_cuenta`),
  ADD UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  ADD UNIQUE KEY `id_empleado` (`id_empleado`);

--
-- Indices de la tabla `empleado`
--
ALTER TABLE `empleado`
  ADD PRIMARY KEY (`id_empleado`),
  ADD UNIQUE KEY `nro_identificacion` (`nro_identificacion`);

--
-- Indices de la tabla `empleado_horario`
--
ALTER TABLE `empleado_horario`
  ADD PRIMARY KEY (`id_empleado`,`id_horario`,`fecha_efectiva`),
  ADD KEY `id_horario` (`id_horario`);

--
-- Indices de la tabla `horario`
--
ALTER TABLE `horario`
  ADD PRIMARY KEY (`id_horario`);

--
-- Indices de la tabla `incidencia`
--
ALTER TABLE `incidencia`
  ADD PRIMARY KEY (`id_incidencia`),
  ADD KEY `id_ruta` (`id_ruta`),
  ADD KEY `id_empleado` (`id_empleado`),
  ADD KEY `id_bus` (`id_bus`);

--
-- Indices de la tabla `incidencia_disciplinaria`
--
ALTER TABLE `incidencia_disciplinaria`
  ADD PRIMARY KEY (`id_incidencia`),
  ADD KEY `id_tipo_disciplinaria` (`id_tipo_disciplinaria`);

--
-- Indices de la tabla `incidencia_operativa`
--
ALTER TABLE `incidencia_operativa`
  ADD PRIMARY KEY (`id_incidencia`);

--
-- Indices de la tabla `mantenimiento`
--
ALTER TABLE `mantenimiento`
  ADD PRIMARY KEY (`id_mantenimiento`),
  ADD KEY `id_bus` (`id_bus`),
  ADD KEY `id_proveedor` (`id_proveedor`),
  ADD KEY `id_tipo_mantenimiento` (`id_tipo_mantenimiento`);

--
-- Indices de la tabla `marca_bus`
--
ALTER TABLE `marca_bus`
  ADD PRIMARY KEY (`id_marca_bus`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `modelo_bus`
--
ALTER TABLE `modelo_bus`
  ADD PRIMARY KEY (`id_modelo_bus`),
  ADD KEY `id_marca_bus` (`id_marca_bus`);

--
-- Indices de la tabla `paradero`
--
ALTER TABLE `paradero`
  ADD PRIMARY KEY (`id_paradero`);

--
-- Indices de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  ADD PRIMARY KEY (`id_proveedor`);

--
-- Indices de la tabla `recorrido`
--
ALTER TABLE `recorrido`
  ADD PRIMARY KEY (`id_recorrido`),
  ADD KEY `id_ruta` (`id_ruta`),
  ADD KEY `id_paradero` (`id_paradero`);

--
-- Indices de la tabla `ruta`
--
ALTER TABLE `ruta`
  ADD PRIMARY KEY (`id_ruta`),
  ADD UNIQUE KEY `codigo_ruta` (`codigo_ruta`);

--
-- Indices de la tabla `supervisor`
--
ALTER TABLE `supervisor`
  ADD PRIMARY KEY (`id_empleado`),
  ADD KEY `id_tipo_supervisor` (`id_tipo_supervisor`);

--
-- Indices de la tabla `supervisor_ruta`
--
ALTER TABLE `supervisor_ruta`
  ADD PRIMARY KEY (`id_empleado`,`id_ruta`,`fecha_asignacion`),
  ADD KEY `id_ruta` (`id_ruta`);

--
-- Indices de la tabla `tipo_disciplinaria`
--
ALTER TABLE `tipo_disciplinaria`
  ADD PRIMARY KEY (`id_tipo_disciplinaria`),
  ADD UNIQUE KEY `nombre_falta` (`nombre_falta`);

--
-- Indices de la tabla `tipo_licencia`
--
ALTER TABLE `tipo_licencia`
  ADD PRIMARY KEY (`id_tipo_licencia`),
  ADD UNIQUE KEY `categoria` (`categoria`,`pais_emision`);

--
-- Indices de la tabla `tipo_mantenimiento`
--
ALTER TABLE `tipo_mantenimiento`
  ADD PRIMARY KEY (`id_tipo_mantenimiento`);

--
-- Indices de la tabla `tipo_supervisor`
--
ALTER TABLE `tipo_supervisor`
  ADD PRIMARY KEY (`id_tipo_supervisor`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `almacen`
--
ALTER TABLE `almacen`
  MODIFY `id_almacen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `asignacion_bus`
--
ALTER TABLE `asignacion_bus`
  MODIFY `id_asignacion_bus` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `bus`
--
ALTER TABLE `bus`
  MODIFY `id_bus` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `bus_ruta`
--
ALTER TABLE `bus_ruta`
  MODIFY `id_bus_ruta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `caja`
--
ALTER TABLE `caja`
  MODIFY `id_caja` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `cuenta_usuario`
--
ALTER TABLE `cuenta_usuario`
  MODIFY `id_cuenta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `empleado`
--
ALTER TABLE `empleado`
  MODIFY `id_empleado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `horario`
--
ALTER TABLE `horario`
  MODIFY `id_horario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `incidencia`
--
ALTER TABLE `incidencia`
  MODIFY `id_incidencia` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `mantenimiento`
--
ALTER TABLE `mantenimiento`
  MODIFY `id_mantenimiento` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `marca_bus`
--
ALTER TABLE `marca_bus`
  MODIFY `id_marca_bus` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `modelo_bus`
--
ALTER TABLE `modelo_bus`
  MODIFY `id_modelo_bus` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `paradero`
--
ALTER TABLE `paradero`
  MODIFY `id_paradero` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  MODIFY `id_proveedor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `recorrido`
--
ALTER TABLE `recorrido`
  MODIFY `id_recorrido` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `ruta`
--
ALTER TABLE `ruta`
  MODIFY `id_ruta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tipo_disciplinaria`
--
ALTER TABLE `tipo_disciplinaria`
  MODIFY `id_tipo_disciplinaria` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tipo_licencia`
--
ALTER TABLE `tipo_licencia`
  MODIFY `id_tipo_licencia` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tipo_mantenimiento`
--
ALTER TABLE `tipo_mantenimiento`
  MODIFY `id_tipo_mantenimiento` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `tipo_supervisor`
--
ALTER TABLE `tipo_supervisor`
  MODIFY `id_tipo_supervisor` smallint(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asignacion_bus`
--
ALTER TABLE `asignacion_bus`
  ADD CONSTRAINT `asignacion_bus_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `asignacion_bus_ibfk_2` FOREIGN KEY (`id_bus`) REFERENCES `bus` (`id_bus`);

--
-- Filtros para la tabla `bus`
--
ALTER TABLE `bus`
  ADD CONSTRAINT `bus_ibfk_1` FOREIGN KEY (`id_modelo_bus`) REFERENCES `modelo_bus` (`id_modelo_bus`),
  ADD CONSTRAINT `bus_ibfk_2` FOREIGN KEY (`id_almacen`) REFERENCES `almacen` (`id_almacen`);

--
-- Filtros para la tabla `bus_ruta`
--
ALTER TABLE `bus_ruta`
  ADD CONSTRAINT `bus_ruta_ibfk_1` FOREIGN KEY (`id_bus`) REFERENCES `bus` (`id_bus`),
  ADD CONSTRAINT `bus_ruta_ibfk_2` FOREIGN KEY (`id_ruta`) REFERENCES `ruta` (`id_ruta`);

--
-- Filtros para la tabla `caja`
--
ALTER TABLE `caja`
  ADD CONSTRAINT `caja_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `caja_ibfk_2` FOREIGN KEY (`id_bus`) REFERENCES `bus` (`id_bus`),
  ADD CONSTRAINT `caja_ibfk_3` FOREIGN KEY (`id_ruta`) REFERENCES `ruta` (`id_ruta`);

--
-- Filtros para la tabla `chofer`
--
ALTER TABLE `chofer`
  ADD CONSTRAINT `chofer_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `chofer_ibfk_2` FOREIGN KEY (`id_tipo_licencia`) REFERENCES `tipo_licencia` (`id_tipo_licencia`);

--
-- Filtros para la tabla `cuenta_usuario`
--
ALTER TABLE `cuenta_usuario`
  ADD CONSTRAINT `cuenta_usuario_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`);

--
-- Filtros para la tabla `empleado_horario`
--
ALTER TABLE `empleado_horario`
  ADD CONSTRAINT `empleado_horario_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `empleado_horario_ibfk_2` FOREIGN KEY (`id_horario`) REFERENCES `horario` (`id_horario`);

--
-- Filtros para la tabla `incidencia`
--
ALTER TABLE `incidencia`
  ADD CONSTRAINT `incidencia_ibfk_1` FOREIGN KEY (`id_ruta`) REFERENCES `ruta` (`id_ruta`),
  ADD CONSTRAINT `incidencia_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `incidencia_ibfk_3` FOREIGN KEY (`id_bus`) REFERENCES `bus` (`id_bus`);

--
-- Filtros para la tabla `incidencia_disciplinaria`
--
ALTER TABLE `incidencia_disciplinaria`
  ADD CONSTRAINT `incidencia_disciplinaria_ibfk_1` FOREIGN KEY (`id_incidencia`) REFERENCES `incidencia` (`id_incidencia`),
  ADD CONSTRAINT `incidencia_disciplinaria_ibfk_2` FOREIGN KEY (`id_tipo_disciplinaria`) REFERENCES `tipo_disciplinaria` (`id_tipo_disciplinaria`);

--
-- Filtros para la tabla `incidencia_operativa`
--
ALTER TABLE `incidencia_operativa`
  ADD CONSTRAINT `incidencia_operativa_ibfk_1` FOREIGN KEY (`id_incidencia`) REFERENCES `incidencia` (`id_incidencia`);

--
-- Filtros para la tabla `mantenimiento`
--
ALTER TABLE `mantenimiento`
  ADD CONSTRAINT `mantenimiento_ibfk_1` FOREIGN KEY (`id_bus`) REFERENCES `bus` (`id_bus`),
  ADD CONSTRAINT `mantenimiento_ibfk_2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`),
  ADD CONSTRAINT `mantenimiento_ibfk_3` FOREIGN KEY (`id_tipo_mantenimiento`) REFERENCES `tipo_mantenimiento` (`id_tipo_mantenimiento`);

--
-- Filtros para la tabla `modelo_bus`
--
ALTER TABLE `modelo_bus`
  ADD CONSTRAINT `modelo_bus_ibfk_1` FOREIGN KEY (`id_marca_bus`) REFERENCES `marca_bus` (`id_marca_bus`);

--
-- Filtros para la tabla `recorrido`
--
ALTER TABLE `recorrido`
  ADD CONSTRAINT `recorrido_ibfk_1` FOREIGN KEY (`id_ruta`) REFERENCES `ruta` (`id_ruta`),
  ADD CONSTRAINT `recorrido_ibfk_2` FOREIGN KEY (`id_paradero`) REFERENCES `paradero` (`id_paradero`);

--
-- Filtros para la tabla `supervisor`
--
ALTER TABLE `supervisor`
  ADD CONSTRAINT `supervisor_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `supervisor_ibfk_2` FOREIGN KEY (`id_tipo_supervisor`) REFERENCES `tipo_supervisor` (`id_tipo_supervisor`);

--
-- Filtros para la tabla `supervisor_ruta`
--
ALTER TABLE `supervisor_ruta`
  ADD CONSTRAINT `supervisor_ruta_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`),
  ADD CONSTRAINT `supervisor_ruta_ibfk_2` FOREIGN KEY (`id_ruta`) REFERENCES `ruta` (`id_ruta`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
