// Etapa de pruebas de API para el Jenkinsfile (pegar dentro de stages { ... }).
// Requiere: agente con Docker y el .env cargado desde credenciales de Jenkins (lo configura Ruth).
// Si la app ya se despliega en una etapa anterior, se puede quitar el "up -d --build" de aqui.
stage('Pruebas de API (Postman + Newman)') {
    steps {
        sh 'docker compose up -d --build'
        sh '''
            for i in $(seq 1 30); do
              docker compose exec -T web python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" && exit 0
              sleep 3
            done
            echo "La app no respondio a tiempo"; exit 1
        '''
        sh 'bash pruebas_api/newman_run.sh'
    }
    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/newman/newman.xml'
            archiveArtifacts artifacts: 'reports/newman/*', allowEmptyArchive: true
            sh 'docker compose down -v || true'
        }
    }
}
