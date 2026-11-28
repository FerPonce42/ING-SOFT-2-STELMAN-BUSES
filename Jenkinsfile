pipeline {
    agent any

    // Issue #61: Pipeline CI/CD en Jenkins disparado por commit
    triggers {
        githubPush()
        pollSCM('* * * * *')
    }

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Descargando últimos cambios desde GitHub...'
                checkout scm
            }
        }

        // Issue #64: Construcción automática (compilación, dependencias y empaquetado)
        stage('2. Construcción: Dependencias y Empaquetado') {
            steps {
                echo 'Instalando dependencias y construyendo paquete/imagen...'
                sh '''
                    if [ ! -f .env ]; then
                        if [ -f .env.example ]; then
                            cp .env.example .env
                        else
                            printf "DB_PASSWORD=stelman_pass\nDB_ROOT_PASSWORD=root_pass\nSECRET_KEY=stelman_secret_key\n" > .env
                        fi
                    fi
                    grep -q "^DB_PASSWORD=" .env || echo "DB_PASSWORD=stelman_pass" >> .env
                    grep -q "^DB_ROOT_PASSWORD=" .env || echo "DB_ROOT_PASSWORD=root_pass" >> .env
                    grep -q "^SECRET_KEY=" .env || echo "SECRET_KEY=stelman_secret_key" >> .env

                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
                    pip install build
                    if [ -f pyproject.toml ]; then python3 -m build; fi
                    docker compose build
                '''
            }
        }

        
        stage('3. Pruebas Unitarias y Cobertura') {
            steps {
                echo 'Ejecutando pruebas unitarias sobre la base de datos CI...'
                sh '''
                    set -eu

                    docker compose -p stelman-buses-ci \
                        -f docker-compose.yml \
                        -f docker-compose.ci.yml \
                        up -d db

                    docker network connect stelman-buses-ci_default jenkins-stelman 2>/dev/null || true

                    . .venv/bin/activate
                    mkdir -p reports

                    PYTHON_DOTENV_DISABLED=1 \
                    DB_HOST=db \
                    DB_PORT=3306 \
                    DB_NAME=bd_stelman_buses_ci \
                    PYTHONPATH=. \
                    python3 -m coverage run -m pytest \
                        --ignore=tests/functional \
                        --junitxml=reports/junit-report.xml

                    PYTHONPATH=. python3 -m coverage xml
                '''
            }
        }

        stage('4. SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis estático con sonar-project.properties...'
                script {
                    if (fileExists('/usr/local/bin/sonar-scanner') || sh(script: 'which sonar-scanner', returnStatus: true) == 0) {
                        withSonarQubeEnv('SonarQube') {
                            sh 'sonar-scanner'
                        }
                    } else {
                        echo 'sonar-scanner no instalado en el agente; verificando sonar-project.properties...'
                        sh 'cat sonar-project.properties'
                    }
                }
            }
        }

        // Issue #65: Gestión de entrega: despliegue automático por CI/CD y con Docker
        
        stage('5. Despliegue Automático con Docker') {
            steps {
                echo 'Desplegando contenedores CI...'
                sh '''
                    docker compose -p stelman-buses-ci \
                        -f docker-compose.yml \
                        -f docker-compose.ci.yml \
                        up -d --build
                '''
            }
        }

        // Issue #62: Pruebas funcionales automatizadas (Selenium) integradas a Jenkins
        stage('6. Pruebas Funcionales (Selenium)') {
            steps {
                echo 'Ejecutando pruebas funcionales con Selenium (Chromium headless en contenedor)...'
                sh '''
                    set -e
                    WEB=$(docker compose ps -q web)
                    rm -rf .ctx-selenium
                    mkdir -p .ctx-selenium reports
                    cp -r tests requirements.txt requirements-dev.txt pytest.ini .ctx-selenium/
                    cp Dockerfile.selenium .ctx-selenium/
                    cp ci/probar_funcionales.sh .ctx-selenium/
                    docker build -f .ctx-selenium/Dockerfile.selenium -t stelman-selenium .ctx-selenium
                    docker rm -f stelman-selenium-run >/dev/null 2>&1 || true
                    set +e
                    docker run --name stelman-selenium-run --network container:$WEB stelman-selenium
                    CODIGO=$?
                    set -e
                    docker cp stelman-selenium-run:/work/reports/funcionales.xml reports/funcionales.xml || true
                    docker rm -f stelman-selenium-run >/dev/null 2>&1 || true
                    exit $CODIGO
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/funcionales.xml'
                }
            }
        }

        // Issue #53: Pruebas de seguridad con OWASP ZAP
        stage('7. Pruebas de Seguridad (OWASP ZAP)') {
            steps {
                echo 'Escaneando la aplicación desplegada con OWASP ZAP (baseline)...'
                sh '''
                    for i in $(seq 1 30); do
                      docker compose exec -T web python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" && break
                      sleep 3
                    done
                    bash pruebas_seguridad/zap_baseline.sh
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/zap/*', allowEmptyArchive: true
                }
            }
        }

        // Issue #54: Pruebas de API con Postman + Newman
        stage('8. Pruebas de API (Postman + Newman)') {
            steps {
                echo 'Ejecutando la colección de Postman con Newman contra la API desplegada...'
                sh '''
                    for i in $(seq 1 30); do
                      docker compose exec -T web python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" && break
                      sleep 3
                    done
                    bash pruebas_api/newman_run.sh
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/newman/newman.xml'
                    archiveArtifacts artifacts: 'reports/newman/*', allowEmptyArchive: true
                }
            }
        }


        // Issue #60: Pruebas de rendimiento JMeter integradas con Jenkins
        stage('9. Pruebas de Rendimiento (JMeter)') {
            steps {
                echo 'Ejecutando pruebas de rendimiento sobre GET /api/v1/caja...'
                withCredentials([usernamePassword(
                    credentialsId: 'jmeter-api-credentials',
                    usernameVariable: 'JMETER_USER',
                    passwordVariable: 'JMETER_PASSWORD'
                )]) {
                    sh '''
                        set -eu

                        mkdir -p reports/jmeter

                        docker compose -p stelman-buses-ci ps -q web

                        NETWORK=$(docker inspect "$WEB" --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' | head -n 1)

                        docker rm -f jmeter-api-caja >/dev/null 2>&1 || true

                        docker create \
                        --name jmeter-api-caja \
                        --network "$NETWORK" \
                        --entrypoint sh \
                        alpine/jmeter:5.6.3 \
                        -c "mkdir -p /tests && sleep 600"

                        docker start jmeter-api-caja
                        docker cp pruebas_rendimiento/plan_api_caja.jmx jmeter-api-caja:/tests/plan_api_caja.jmx

                        docker exec jmeter-api-caja \
                            /opt/apache-jmeter-5.6.3/bin/jmeter \
                            -n \
                            -t /tests/plan_api_caja.jmx \
                            -Jhost=web \
                            -Jport=5000 \
                            -Jusuario="$JMETER_USER" \
                            -Jclave="$JMETER_PASSWORD" \
                            -Jthreads=100 \
                            -Jrampup=10 \
                            -l /tests/resultados.jtl

                        docker cp jmeter-api-caja:/tests/resultados.jtl reports/jmeter/resultados.jtl

                        docker exec jmeter-api-caja \
                            /opt/apache-jmeter-5.6.3/bin/jmeter \
                            -g /tests/resultados.jtl \
                            -o /tests/reporte_html

                        docker cp jmeter-api-caja:/tests/reporte_html reports/jmeter/reporte_html

                        docker rm -f jmeter-api-caja >/dev/null

                        echo "Pruebas JMeter finalizadas correctamente"
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/jmeter/**', allowEmptyArchive: true
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline ejecutado con éxito. Aplicación desplegada en http://localhost:5000"
        }
        // Issue #63: gestión de cambios automatizada (issue en GitHub + aviso al equipo)
        failure {
            echo "Fallo detectado en el pipeline. Revisa el detalle en la consola de Jenkins."
        }
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit-report.xml'
        }
    }
}