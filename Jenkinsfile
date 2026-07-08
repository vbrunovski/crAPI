pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем --config auto, чтобы избежать проблем с сетью при скачивании
                    // Перенаправляем stdout в файл, чтобы обойти проблемы с правами записи
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan --config auto --exclude semgrep-report.json --json /src > "${WORKSPACE}/semgrep-report.json"
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