pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
    steps {
        script {
            sh '''
                echo "--- Проверка прав на файлы ---"
                ls -l /var/jenkins_home/workspace/sast1/services/identity/src/main/java/com/crapi/controller/AuthController.java
                
                echo "--- Проверка через контейнер (кто я и что вижу) ---"
                docker run --rm \
                -v "${WORKSPACE}:/src" \
                returntocorp/semgrep \
                sh -c "whoami && ls -R /src/services/identity | head -n 20"
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