pipeline {
    agent any
    
    stages {
        // 1. Статическое сканирование кода
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

        // 2. Поднятие инфраструктуры для DAST
        stage('Deploy App') {
            steps {
                script {
                    // Поднимаем crAPI в фоне. Путь к compose файлу должен быть верным
                    sh 'docker-compose -f deploy/docker-compose.yml up -d'
                    // Важно: ждем, пока сервисы реально поднимутся
                    sh 'sleep 40' 
                }
            }
        }

        // 3. Динамическое сканирование работающего API
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

        // 4. Очистка ресурсов
        stage('Cleanup') {
            always {
                sh 'docker-compose -f deploy/docker-compose.yml down'
            }
        }
        
        // 5. Сбор результатов
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json, nuclei_report.txt', allowEmptyArchive: true
            }
        }
    }
}