pipeline {
    agent any
    
    stages {
        // 1. Статический анализ кода (SAST)
        stage('SAST - Code Scan') {
            steps {
                script {
                    sh 'tar -cf - services/identity | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config auto --no-git-ignore --json services/identity" > "${WORKSPACE}/semgrep-report.json"'
                }
            }
        }

        // 2. Динамический анализ уже поднятого стенда (DAST)
        // 2. Динамический анализ уже поднятого стенда (DAST)
        stage('DAST - API Scan') {
            steps {
                script {
                    // Запускаем Nuclei и сразу после этого меняем права на созданный файл
                    sh '''
                    docker run --rm --network host -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest \
                        -target http://localhost:8888 \
                        -severity medium,high,critical \
                        -o /output/nuclei_report.txt
                    
                    # Даем Jenkins полные права на чтение этого файла
                    sudo chmod 666 "${WORKSPACE}/nuclei_report.txt" || chmod 666 "${WORKSPACE}/nuclei_report.txt" || true
                    '''
                }
            }
        }
        
        // 3. Публикация отчетов в интерфейс Jenkins
        stage('Archive Security Reports') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json, nuclei_report.txt', allowEmptyArchive: true
            }
        }
    }
}