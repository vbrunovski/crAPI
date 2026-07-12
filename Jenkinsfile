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
                    echo "--- Запуск crAPI напрямую через docker run ---"
                    // Создаем общую сеть, чтобы контейнеры видели друг друга
                    sh 'docker network create crapi-net || true'
                    
                    // Поднимаем базу данных (опционально, но нужно для старта identity)
                    sh 'docker run -d --name crapi-db --network crapi-net -e POSTGRES_USER=crapi -e POSTGRES_PASSWORD=crapi postgres:15-alpine || true'
                    
                    // Поднимаем основной web-интерфейс/gateway crAPI на порту 8080
                    sh 'docker run -d --name crapi-web --network crapi-net -p 8080:8080 ntop/crapi-web:latest || true'
                    
                    echo "--- Ожидание инициализации сервисов ---"
                    sh 'sleep 30' 
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
            steps {
                script {
                    sh '''
                    echo "--- Запуск Nuclei ---"
                    # Сканируем через общую сеть docker хоста
                    docker run --rm --network host -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest \
                        -target http://localhost:8080 \
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