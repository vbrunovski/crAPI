pipeline {
    agent any
    stages {
        stage('SAST - Semgrep') {
            steps {
  script {
    sh '''
        # Запускаем сканер, используя официальный реестр правил Semgrep (он не требует локального файла)
        # Это гарантированно работает, так как контейнер сам тянет правила из сети
        docker run --rm \
        -v "${WORKSPACE}:/src" \
        returntocorp/semgrep \
        semgrep scan --config auto --json /src > "${WORKSPACE}/semgrep-report.json" || true
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