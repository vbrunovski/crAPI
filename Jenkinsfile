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
    docker run --rm \
    -v "${WORKSPACE}:/src" \
    returntocorp/semgrep \
    semgrep scan \
        --config auto \
        --no-git-ignore \
        --json \
        /src/services > "${WORKSPACE}/semgrep-report.json"
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