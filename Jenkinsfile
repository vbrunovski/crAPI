pipeline {
    agent any
    
    stages {
        stage('SAST - Identity Service Only') {
    steps {
        script {
            // Мы сканируем файлы текущей директории Jenkins и передаем их в контейнер через tar
            // Это обходит все проблемы с маунтами
            sh '''
                echo "--- Сканирование через передачу архива ---"
                tar -cf - services/identity | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config auto --no-git-ignore --json services/identity" > "${WORKSPACE}/semgrep-report.json"
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