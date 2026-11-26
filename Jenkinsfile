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
                echo 'Ejecutando pruebas automatizadas (excluyendo funcionales) y generando coverage.xml...'
                sh '''
                    set -a
                    . ./.env
                    set +a
                    docker compose up -d db
                    sleep 12
                    . .venv/bin/activate
                    mkdir -p reports
                    DB_HOST=host.docker.internal DB_PORT=3307 PYTHONPATH=. python3 -m coverage run -m pytest --ignore=tests/functional --junitxml=reports/junit-report.xml
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
                echo 'Desplegando contenedores actualizados en el puerto 5000...'
                sh '''
                    docker compose down
                    docker compose up -d --build
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
    }

    post {
        success {
            echo "Pipeline ejecutado con éxito. Aplicación desplegada en http://localhost:5000"
        }
        // Issue #63: gestión de cambios automatizada (issue en GitHub + aviso al equipo)
        failure {
            echo "Fallo detectado en el pipeline. Revisa el detalle en la consola de Jenkins."
            withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                sh 'python3 ci/crear_issue_fallo.py || echo "No se pudo crear el issue automático"'
            }
        }
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit-report.xml'
        }
    }
}