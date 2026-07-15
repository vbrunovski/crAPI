pipeline {
    agent any
    
    stages {
        stage('SAST - Code Scan') {
            steps {
                script {
                    // Упаковываем всё, включая .semgrep, распаковываем в корень контейнера и запускаем из корня
                    sh 'tar -cf - services/identity .semgrep | docker run --rm -i returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config .semgrep --json services/identity" > "${WORKSPACE}/semgrep-report.json" || true'
                }
            }
        }

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

        stage('SCA Scan (Trivy)') {
            steps {
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "${WORKSPACE}":/apps aquasec/trivy:latest fs --exit-code 1 --severity HIGH,CRITICAL /apps'
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