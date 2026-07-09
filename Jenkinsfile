pipeline {
    agent any
    
    stages {
      stage('SAST - Semgrep') {
    steps {
        script {
            sh '''
                # Используем переменную ${WORKSPACE}, которая в Jenkins всегда указывает на правильный путь
                # Пробуем смонтировать WORKSPACE как есть
                docker run --rm \
                -v "${WORKSPACE}:/src" \
                -w "/src" \
                returntocorp/semgrep \
                semgrep scan --config auto --no-git-ignore --json services/identity > "${WORKSPACE}/semgrep-report.json" || true
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