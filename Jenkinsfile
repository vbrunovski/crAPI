pipeline {
    agent any
    
    stages {
        // 1. Статический анализ кода (SAST)
        stage('SAST - Code Scan') {
            steps {
                script {
                    // Упаковываем файлы, распаковываем в контейнере и пишем отчет в JSON
                    sh 'tar -cf - services/identity .semgrep | docker run --rm -i returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config .semgrep --json services/identity" > "${WORKSPACE}/semgrep-report.json" || true'
                }
            }
        }

        // 2. Динамический анализ API (DAST)
        stage('DAST - API Scan') {
            steps {
                script {
                    // Монтируем папку для кэша шаблонов, чтобы не качать их заново каждый раз,
                    // и добавляем || true в конце, чтобы сетевые сбои не рушили пайплайн
                    sh '''
                    docker run --rm --network host \
                        -v "${WORKSPACE}/.nuclei-templates":/root/nuclei-templates \
                        projectdiscovery/nuclei:latest \
                        -target http://localhost:8888 \
                        -severity medium,high,critical > "${WORKSPACE}/nuclei_report.txt" || true
                    '''
                }
            }
        }

      // 3. Анализ сторонних зависимостей (SCA)
        stage('SCA Scan (Trivy)') {
            steps {
                script {
                    sh '''
                    docker run --rm \
                        -e TRIVY_DB_REPOSITORY="public.ecr.aws/aquasecurity/trivy-db" \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v "${WORKSPACE}":/workspace \
                        -v "${WORKSPACE}/.trivy-cache":/root/.cache/trivy \
                        -w /workspace \
                        aquasec/trivy:latest fs \
                        --scanners vuln \
                        --vuln-type os,library \
                        --timeout 20m \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --format json \
                        -o trivy-report.json \
                        /workspace
                    '''
                }
            }
        }

        // 4. Публикация отчетов в интерфейс Jenkins
        stage('Archive Security Reports') {
            steps {
                // Добавлен trivy-report.json в список архивируемых файлов
                archiveArtifacts artifacts: 'semgrep-report.json, nuclei_report.txt, trivy-report.json', allowEmptyArchive: true
            }
        }
    }
}