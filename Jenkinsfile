pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            stage('SAST - Semgrep') {
    steps {
        script {
            sh '''
                # Запускаем сканер
                docker run --rm -v "${WORKSPACE}:/src" returntocorp/semgrep \
                semgrep scan --config /src/semgrep.yaml --json --output /src/semgrep-report.json /src || true
                
                # СРАЗУ меняем владельца и права, чтобы Jenkins мог прочитать файл
                chmod 666 "${WORKSPACE}/semgrep-report.json"
            '''
        }
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