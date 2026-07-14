pipeline {
    agent any
    
    stages {
        // 1. Статический анализ кода (SAST)
        stage('SAST - Code Scan') {
            steps {
                script {
                    // Архивируем и код, и ваши правила из папки .semgrep
                    sh 'tar -cf - services/identity .semgrep | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config .semgrep --json services/identity" > "${WORKSPACE}/semgrep-report.json"'
                }
            }
        }

        // 2. Динамический анализ уже поднятого стенда (DAST)
        // 2. Динамический анализ уже поднятого стенда (DAST)
        stage('DAST - API Scan') {
            steps {
                script {
                    // Убираем монтирование папок (-v) и флаг -o. 
                    // Просто перенаправляем весь поток вывода контейнера в файл на хосте через '>'
                    sh '''
                    docker run --rm --network host projectdiscovery/nuclei:latest \
                        -target http://localhost:8888 \
                        -severity medium,high,critical > "${WORKSPACE}/nuclei_report.txt"
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