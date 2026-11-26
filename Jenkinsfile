pipeline {
    agent any

    // Issue #61: Pipeline CI/CD en Jenkins disparado por commit
    triggers {
        githubPush()
        pollSCM('* * * * *')
    }

    environment {
        SONAR_PROJECT_KEY = "ING-SOFT-2-STELMAN-BUSES"
    }

    stages {
        stage('1. Checkout') {
            steps {
                echo 'Descargando últimos cambios desde GitHub...'
                checkout scm
            }
        }

        // Issue 2: Construcción automática (compilación, dependencias y empaquetado)
        stage('2. Construcción: Dependencias y Empaquetado') {
            steps {
                echo 'Instalando dependencias y construyendo paquete/imagen...'
                bat '''
                    if not exist .venv (python -m venv .venv)
                    call .venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    if exist requirements-dev.txt (pip install -r requirements-dev.txt)
                    pip install build
                    if exist pyproject.toml (python -m build)
                    docker compose build
                '''
            }
        }

        stage('3. Pruebas Automatizadas y Cobertura') {
            steps {
                echo 'Ejecutando pruebas automatizadas con pytest...'
                bat '''
                    call .venv\\Scripts\\activate.bat
                    if not exist reports mkdir reports
                    pytest tests/unit tests/integration --cov=app --cov-report=xml:reports/coverage.xml --junitxml=reports/junit-report.xml
                '''
            }
        }

        stage('4. Análisis Estático (SonarQube)') {
            steps {
                echo 'Analizando calidad de código en SonarQube...'
                withSonarQubeEnv('SonarQubeServer') {
                    bat '''
                        sonar-scanner -Dsonar.projectKey=%SONAR_PROJECT_KEY% -Dsonar.sources=app -Dsonar.python.coverage.reportPaths=reports/coverage.xml
                    '''
                }
            }
        }

        // Issue 3: Gestión de entrega: despliegue automático por CI/CD y con Docker
        stage('5. Despliegue Automático con Docker') {
            steps {
                echo 'Desplegando contenedores actualizados en el puerto 5000...'
                bat '''
                    docker compose down
                    docker compose up -d
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline ejecutado con éxito. Aplicación desplegada en http://localhost:5000"
        }
        failure {
            echo "Fallo detectado en el pipeline. Revisa el detalle en la consola de Jenkins."
        }
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit-report.xml'
        }
    }
}