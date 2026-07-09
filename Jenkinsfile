pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем --no-git-ignore для полной видимости всех файлов
                    // Используем > для записи файла на хост (обход прав контейнера)
                    // Добавили --exclude, чтобы не сканировать сам отчет
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config auto \
                            --no-git-ignore \
                            --exclude semgrep-report.json \
                            --json \
                            /src > "${WORKSPACE}/semgrep-report.json" || true
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                // Если файл пустой или с ошибками, Jenkins его все равно заархивирует
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                echo 'SAST scan completed and report archived.'
            }
        }
    }
}