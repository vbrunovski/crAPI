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
                    // Используем --config p/owasp-top-10
                    // Добавили ls -l для проверки наличия файла сразу после скана
                    sh '''
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan --config p/owasp-top-10 --json --output /src/semgrep-report.json /src || true
                        
                        echo "--- Debug: Checking if file exists in workspace ---"
                        ls -l "${WORKSPACE}/semgrep-report.json" || echo "File still not found!"
                    '''
                }
            }
        }
        stage('Archive Report') {
            steps {
                // Если файл существует, он будет заархивирован
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
            }
        }
    }
}