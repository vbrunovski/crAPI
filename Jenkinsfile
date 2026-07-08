pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    echo "=== Installing Semgrep ==="
                    
                    # Проверяем, установлен ли pip
                    if ! command -v pip3 &> /dev/null; then
                        echo "Installing pip..."
                        apt-get update && apt-get install -y python3-pip
                    fi
                    
                    pip3 install semgrep --quiet
                    
                    echo "=== Running Semgrep SAST Scan ==="
                    semgrep --config=p/owasp-top-10 \
                            --config=auto \
                            --output=semgrep-report.json \
                            --format=json \
                            .
                '''
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', fingerprint: true
                echo 'SAST scan completed!'
            }
        }
    }
}