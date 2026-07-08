pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    echo "=== Semgrep SAST Scan ==="
                    
                    # Проверяем, установлен ли Semgrep
                    if command -v semgrep > /dev/null; then
                        semgrep --config=p/owasp-top-10 \
                                --config=auto \
                                --output=semgrep-report.json \
                                --format=json \
                                .
                    else
                        echo "Semgrep not installed in this Jenkins agent."
                        echo "Please install Semgrep on Jenkins or use Docker agent."
                        touch semgrep-report.json
                    fi
                '''
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', fingerprint: true, allowEmptyArchive: true
                echo 'SAST stage completed.'
            }
        }
    }
}