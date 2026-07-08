pipeline {
    agent any // Запускаем на любом агенте

    stages {
        stage('SAST - Semgrep') {
            steps {
                // Если нет Docker CLI, мы не вызываем docker
                // Вызываем semgrep напрямую через shell
                sh 'semgrep --config=p/owasp-top-10 --output=semgrep-report.json --format=json .'
            }
        }
    }
}