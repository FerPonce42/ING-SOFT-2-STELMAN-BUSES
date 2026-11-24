// Etapa de seguridad para el Jenkinsfile (pegar dentro de stages { ... }).
// Requiere: agente con Docker, y el .env cargado desde credenciales de Jenkins (lo configura Ruth).
// Si el pipeline ya despliega la app en una etapa anterior, se puede quitar el "up -d --build" de aqui.
stage('Pruebas de seguridad (OWASP ZAP)') {
    steps {
        sh 'docker compose up -d --build'
        // Espera a que la app responda (maximo ~90 s)
        sh '''
            for i in $(seq 1 30); do
              docker compose exec -T web python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" && exit 0
              sleep 3
            done
            echo "La app no respondio a tiempo"; exit 1
        '''
        sh 'bash pruebas_seguridad/zap_baseline.sh'
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/zap/*', allowEmptyArchive: true
            sh 'docker compose down -v || true'
        }
    }
}
