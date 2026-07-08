pipeline {
    agent {
        docker {
            image 'returntocorp/semgrep'
            // Используем args для монтирования текущей директории с правильными правами
            args '-u root -v "${WORKSPACE}:/src"' 
        }
    }
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    echo "=== Semgrep Scan Starting ==="
                    # Semgrep по умолчанию сканирует текущую папку
                    semgrep --config=p/owasp-top-10 \
                            --output=semgrep-report.json \
                            --format=json
                    echo "=== Scan Finished ==="
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
            }
        }
    }
}