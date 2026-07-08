pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем перенаправление потока (>) вместо аргумента --output
                    // Это гарантирует, что файл создастся на хосте под пользователем Jenkins
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan --config /src/semgrep.yaml --json /src > "${WORKSPACE}/semgrep-report.json" || true
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