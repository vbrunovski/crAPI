pipeline {
    agent any // Запуск прямо на агенте (без docker-обертки)
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    # Установка семантического анализатора
                    python3 -m pip install semgrep
                    
                    echo "=== Semgrep SAST Scan Started ==="
                    semgrep --config=p/owasp-top-10 \
                            --config=auto \
                            --output=semgrep-report.json \
                            --format=json \
                            .
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