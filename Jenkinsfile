pipeline {
    agent {
        docker {
            image 'returntocorp/semgrep'
            args '--user root -v /var/run/docker.sock:/var/run/docker.sock'
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
                archiveArtifacts artifacts: 'semgrep-report.json', fingerprint: true, allowEmptyArchive: true
                echo 'SAST scan completed successfully!'
            }
        }
    }
}