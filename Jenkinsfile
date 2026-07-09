pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Мы используем -w /src/services, чтобы сделать эту папку рабочей директорией контейнера
                    // Тогда `semgrep scan .` будет сканировать именно её
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        -w "/src/services" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config auto \
                            --no-git-ignore \
                            --exclude semgrep-report.json \
                            --json \
                            . > "${WORKSPACE}/semgrep-report.json" || true
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
            }
        }
    }
}