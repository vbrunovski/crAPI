pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // 1. Мы явно указываем -w (working directory) в /src/services
                    // 2. Мы перенаправляем stdout в файлsemgrep-report.json
                    // 3. Используем --json без --output, чтобы stdout шел прямо в наш файл
                    sh '''
                        echo "--- Начинаем сканирование сервисов ---"
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        -w "/src/services" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config auto \
                            --no-git-ignore \
                            --json \
                            . > "${WORKSPACE}/semgrep-report.json"
                        
                        echo "--- Проверка размера отчета ---"
                        ls -lh "${WORKSPACE}/semgrep-report.json"
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                // Теперь файл точно будет на диске
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: false
            }
        }
    }
}