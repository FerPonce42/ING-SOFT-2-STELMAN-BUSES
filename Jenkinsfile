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
                    . .venv/bin/activate
                    mkdir -p reports
                    python3 -m coverage run -m pytest --ignore=tests/functional --junitxml=reports/junit-report.xml
                    python3 -m coverage xml
                '''
            }
        }

        stage('4. SonarQube Analysis') {
            steps {
                echo 'Ejecutando análisis estático con sonar-project.properties...'
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner
                    '''
                }
            }
        }

        // Issue #65: Gestión de entrega: despliegue automático por CI/CD y con Docker
        stage('5. Despliegue Automático con Docker') {
            steps {
                echo 'Desplegando contenedores actualizados en el puerto 5000...'
                sh '''
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