pipeline {
    agent any
    
    stages {
        stage('SAST - Identity Service') {
            steps {
                script {
                    sh '''
                        echo "--- Сканирование через передачу архива ---"
                        tar -cf - services/identity | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config auto --no-git-ignore --json services/identity" > "${WORKSPACE}/semgrep-report.json"
                    '''
                }
            }
        }

        stage('Deploy App') {
            steps {
                script {
                    sh 'docker-compose -f deploy/docker-compose.yml up -d'
                    sh 'sleep 40' 
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
            steps {
                script {
                    sh '''
                    echo "--- Запуск Nuclei ---"
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
    
    // Вот здесь правильное место для блока post
    post {
        always {
            echo 'Очистка ресурсов...'
            sh 'docker-compose -f deploy/docker-compose.yml down'
        }
    }
}