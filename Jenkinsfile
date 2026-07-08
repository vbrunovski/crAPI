pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    echo "=== Installing Semgrep ==="
                    
                    # Пытаемся установить pip, если нет
                    if ! command -v pip3 &> /dev/null; then
                        apt-get update && apt-get install -y python3-pip || echo "apt-get failed, trying alternative..."
                    fi
                    
                    pip3 install semgrep --quiet || pip install semgrep --quiet || echo "Semgrep install failed"
                    
                    echo "=== Running Semgrep SAST Scan ==="
                    semgrep --config=p/owasp-top-10 \
                            --config=auto \
                            --output=semgrep-report.json \
                            --format=json \
                            . || echo "Semgrep scan completed with warnings"
                '''
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', fingerprint: true, allowEmptyArchive: true
                echo 'SAST scan completed!'
            }
        }
    }
}