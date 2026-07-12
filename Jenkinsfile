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
                    // Используем универсальный контейнер для запуска docker-compose, чтобы не зависеть от окружения
                    sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "${WORKSPACE}:/app" -w /app docker/compose:latest -f deploy/docker-compose.yml up -d'
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
            sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "${WORKSPACE}:/app" -w /app docker/compose:latest -f deploy/docker-compose.yml down'
        }
    }
}