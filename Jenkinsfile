pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SAST - Semgrep Scan') {
            steps {
                script {
                    // Установка Semgrep
                    sh 'pip install semgrep --quiet'
                    
                    // Основной скан
                    sh '''
                        semgrep --config=p/owasp-top-10 \
                                --config=auto \
                                --output=semgrep-results.json \
                                --format=json \
                                .
                    '''
                }
            }
        }
        
        stage('SAST Report') {
            steps {
                script {
                    // Показываем количество critical/high findings
                    sh '''
                        echo "=== Semgrep Results ==="
                        jq '.results | length' semgrep-results.json || echo "0"
                    '''
                }
                archiveArtifacts artifacts: 'semgrep-results.json', fingerprint: true
            }
        }
    }
    
    post {
        always {
            // Публикация отчёта
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'semgrep-results.json',
                reportName: 'Semgrep SAST Report'
            ])
        }
        failure {
            echo 'SAST scan failed - check the logs'
        }
    }
}