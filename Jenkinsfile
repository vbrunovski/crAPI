pipeline {
    agent {
        docker {
            image 'returntocorp/semgrep'
            args '--user root'
        }
    }
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
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
                echo 'SAST scan completed successfully!'
            }
        }
    }
}