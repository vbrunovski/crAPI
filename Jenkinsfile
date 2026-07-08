pipeline {
    agent any
    stages {
        stage('SAST') {
            steps {
                sh 'semgrep --config=p/owasp-top-10 --output=semgrep-report.json --format=json .'
            }
        }
    }
}