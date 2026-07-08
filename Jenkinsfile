pipeline {
    agent {
        docker {
            image 'returntocorp/semgrep'
            // Используем -u root, чтобы избежать проблем с правами доступа к файлам в воркспейсе
            args '-u root' 
        }
    }
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    echo "=== Semgrep SAST Scan Started ==="
                    semgrep --config=p/owasp-top-10 \
                            --config=auto \
                            --output=semgrep-report.json \
                            --format=json \
                            .
                    echo "=== Scan Completed ==="
                '''
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                echo 'SAST report archived.'
            }
        }
    }
}