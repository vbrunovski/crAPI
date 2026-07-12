pipeline {
    agent any
    
    stages {
        stage('SAST - Identity Service') {
            steps {
                script {
                    sh 'tar -cf - services/identity | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config auto --no-git-ignore --json services/identity" > "${WORKSPACE}/semgrep-report.json"'
                }
            }
        }

        stage('Deploy App Test Стенд') {
            steps {
                script {
                    echo "--- Развертывание реальных контейнеров crAPI ---"
                    sh 'docker network create crapi-net || true'
                    
                    // Запуск базы данных
                    sh 'docker run -d --name crapi-db --network crapi-net -e POSTGRES_USER=crapi -e POSTGRES_PASSWORD=crapi postgres:15-alpine || true'
                    
                    // Используем ОФИЦИАЛЬНЫЙ публичный образ crAPI Web Gateway. Внутри он слушает порт 80.
                    sh 'docker run -d --name crapi-web --network crapi-net -p 8888:80 defendagainstattacks/crapi-web:latest'
                    
                    echo "--- Ожидание инициализации сервисов ---"
                    sh 'sleep 40' 
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
            steps {
                script {
                    echo "--- Запуск Nuclei против crAPI Web ---"
                    // Стучимся во внутренний порт 80 контейнера crapi-web
                    sh '''
                    docker run --rm --network crapi-net -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest \
                        -target http://crapi-web:80 \
                        -severity medium,high,critical \
                        -o /output/nuclei_report.txt -v
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json, nuclei_report.txt', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo 'Очистка тестового стенда...'
            sh '''
            docker stop crapi-web crapi-db || true
            docker rm crapi-web crapi-db || true
            docker network rm crapi-net || true
            '''
        }
    }
}