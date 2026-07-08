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
                    // Сканирование
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan --config /src/semgrep.yaml --json --output /src/semgrep-report.json /src || true
                        
                        # Даем права на файл, чтобы Jenkins мог его прочитать
                        chmod 666 "${WORKSPACE}/semgrep-report.json"
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