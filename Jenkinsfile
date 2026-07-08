pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            steps {
                // Это сработает, потому что теперь внутри Jenkins есть docker-клиент
                sh 'docker run --rm -v "${WORKSPACE}:/src" returntocorp/semgrep semgrep --config=p/owasp-top-10 --output=/src/semgrep-report.json --format=json /src'
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
            }
        }
    }
}