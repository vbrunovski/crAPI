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

        stage('Deploy App') {
            steps {
                script {
                    echo "--- Развертывание контейнеров crAPI напрямую ---"
                    // Читаем docker-compose.yml из репозитория и передаем его в стандартный docker compose хоста без маунтов директорий
                    sh 'cat deploy/docker-compose.yml | docker compose -f - up -d'
                    
                    echo "--- Ожидание инициализации API сервисов ---"
                    sh 'sleep 40' 
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
            steps {
                script {
                    sh 'docker run --rm --network host -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest -target http://localhost:8080 -severity medium,high,critical -o /output/nuclei_report.txt -v'
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
            echo 'Очистка ресурсов...'
            // Удаляем контейнеры, передавая файл через пайплайн
            sh 'cat deploy/docker-compose.yml | docker compose -f - down'
        }
    }
}