pipeline {
    agent any

    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Добавили флаг -u 1000:1000, чтобы контейнер писал файлы от имени пользователя jenkins
                    sh '''
                        docker run --rm \
                        -u $(id -u):$(id -g) \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config=p/owasp-top-10 \
                            --json \
                            --output=/src/semgrep-report.json \
                            /src
                    '''
                }
            }
        }

        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                echo 'SAST report successfully archived.'
            }
        }
    }
}