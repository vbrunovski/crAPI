pipeline {
    agent any
    
    stages {
    // 1. Статический анализ кода (SAST)
// 1. Статический анализ кода (SAST)
        stage('SAST - Code Scan') {
            steps {
                script {
                    // Исправили двойной дефис в --no-error
                    sh 'docker run --rm -v "${WORKSPACE}:/src" -w /src returntocorp/semgrep semgrep scan --config .semgrep --json services/identity --no-error > "${WORKSPACE}/semgrep-report.json"'
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