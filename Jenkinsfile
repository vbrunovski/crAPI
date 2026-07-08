pipeline {
    agent any

    stages {
        stage('Prepare Permissions') {
            steps {
                sh 'chmod -R 777 "${WORKSPACE}"'
            }
        }
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем --config auto вместо p/owasp-top-10
                    // Это заставит Semgrep использовать встроенные правила без скачивания
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config p/owasp-top-10 \
                            --json \
                            --output /src/semgrep-report.json \
                            /src || true
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