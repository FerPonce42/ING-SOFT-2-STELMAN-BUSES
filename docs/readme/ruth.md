# Documentación de CI/CD, Construcción y Despliegue Automatizado — Stelman Buses

**Responsable:** Ruth Mery Benique Huaman  
**Rama de trabajo:** `feature/cicd-docker-buses`  
**Issues asociados:** `#61`, `#64`, `#65`

---

## 1. Resumen de Implementación

Se implementó un flujo completo de Integración Continua y Entrega Continua (**CI/CD**) utilizando **Jenkins** y **Docker Compose** para automatizar la validación, construcción, pruebas unitarias y despliegue de la aplicación web **Stelman Buses** (`http://localhost:5000`).

| Issue | Requisito Cubierto | Implementación Técnica |
| :--- | :--- | :--- |
| **#61** | Pipeline CI/CD en Jenkins disparado por commit | `Jenkinsfile` declarativo con triggers `githubPush()` y `pollSCM('* * * * *')` conectado a la rama `feature/cicd-docker-buses`. |
| **#64** | Construcción automática (dependencias y empaquetado) | Creación de entorno virtual `.venv`, instalación de `requirements.txt` y `requirements-dev.txt`, empaquetado con `build` y construcción de imagen con `docker compose build`. |
| **#65** | Despliegue automático con Docker y documentación | Orquestación automática de contenedores (`db` MariaDB y `web` Flask) mediante `docker compose up -d --build` en el puerto `5000`. |

---

## 2. Estructura del Pipeline (`Jenkinsfile`)

El pipeline consta de **5 etapas secuenciales** y acciones posteriores (`post`):

1. **`1. Checkout`:** Descarga los últimos cambios desde el repositorio `FerPonce42/ING-SOFT-2-STELMAN-BUSES` en la rama `feature/cicd-docker-buses`.
2. **`2. Construcción: Dependencias y Empaquetado`:**
   - Verifica o genera el archivo `.env` a partir de `.env.example` con las variables requeridas (`DB_PASSWORD`, `DB_ROOT_PASSWORD`, `SECRET_KEY`).
   - Crea el entorno aislado `.venv`, actualiza `pip`, instala las dependencias de producción y desarrollo, ejecuta el empaquetado y construye las imágenes Docker (`docker compose build`).
3. **`3. Pruebas Unitarias y Cobertura`:**
   - Levanta el servicio de base de datos MariaDB (`docker compose up -d db`).
   - Ejecuta la suite de pruebas automatizadas con `pytest` (excluyendo pruebas funcionales de navegador) y genera los reportes `reports/junit-report.xml` y `coverage.xml`.
4. **`4. SonarQube Analysis`:** Verifica la configuración de `sonar-project.properties` y ejecuta `sonar-scanner` cuando está disponible en el agente.
5. **`5. Despliegue Automático con Docker`:** Detiene instancias previas (`docker compose down`) y despliega la versión actualizada en segundo plano (`docker compose up -d --build`).
6. **Post Actions:** Publica los resultados de pruebas JUnit en el historial de ejecuciones de Jenkins.

---

## 3. Guía de Ejecución y Verificación Local

### Requisitos previos
- **Docker Desktop** activo en el equipo.
- Contenedor de **Jenkins** conectado al socket de Docker (`-v //var/run/docker.sock:/var/run/docker.sock`) en `http://localhost:8080`.

### Pasos de verificación
1. Realizar un cambio en el código fuente o configuración y subirlo al repositorio remoto:
   ```bash
   git add .
   git commit -m "feat(ci): actualizar configuración del sistema"
   git push origin feature/cicd-docker-buses
   