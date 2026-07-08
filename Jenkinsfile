pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем конфиг из самого репозитория (он уже внутри /src)
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan --config /src/semgrep.yaml --json --output /src/semgrep-report.json /src || true
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