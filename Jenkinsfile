pipeline {
    agent any

    stages {
        stage('Prepare Permissions') {
            steps {
                // Делаем папку доступной для записи всем пользователям, 
                // прежде чем запускать сканер
                sh 'chmod -R 777 "${WORKSPACE}"'
            }
        }
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Убираем флаг -u, чтобы контейнер работал от root (он сам разберется),
                    // раз мы уже открыли права на папку на хосте
                    sh '''
                        docker run --rm \
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
            }
        }
    }
}