pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    sh '''
                        echo "--- Скан запускается ---"
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan --config /src/semgrep.yaml --json --output /src/semgrep-report.json /src || true
                        
                        echo "--- Debug: Листинг папки /src внутри контейнера ---"
                        docker run --rm -v "${WORKSPACE}:/src" returntocorp/semgrep ls -l /src
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