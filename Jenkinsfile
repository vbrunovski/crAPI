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
                    echo "--- Развертывание контейнеров crAPI в изолированной сети ---"
                    sh 'docker network create crapi-net || true'
                    sh 'docker run -d --name crapi-db --network crapi-net -e POSTGRES_USER=crapi -e POSTGRES_PASSWORD=crapi postgres:15-alpine || true'
                    
                    // Меняем внешний порт на 8888, чтобы не конфликтовать с Jenkins (8080)
                    sh 'docker run -d --name crapi-web --network crapi-net -p 8888:8888 ntop/crapi-web:latest || true'
                    
                    echo "--- Ожидание инициализации сервисов ---"
                    sh 'sleep 40' 
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
            steps {
                script {
                    echo "--- Запуск Nuclei против crAPI ---"
                    // Запускаем Nuclei в той же Docker-сети (crapi-net) 
                    // и указываем в качестве таргета имя контейнера 'crapi-web' и его внутренний порт
                    sh '''
                    docker run --rm --network crapi-net -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest \
                        -target http://crapi-web:8888 \
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