pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем --config auto (он сам подхватит все языки в проекте)
                    // Указываем /src/services как точку входа для анализа
                    // --no-git-ignore нужен, потому что мы в контейнере и git-index может быть недоступен
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config auto \
                            --no-git-ignore \
                            --exclude semgrep-report.json \
                            --json \
                            /src/services > "${WORKSPACE}/semgrep-report.json" || true
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