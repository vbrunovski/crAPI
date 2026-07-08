pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                sh '''
                    echo "=== Trying to run Semgrep ==="
                    
                    # Попытка 1: Docker
                    if command -v docker > /dev/null; then
                        docker run --rm -v "$(pwd):/src" returntocorp/semgrep semgrep --config=p/owasp-top-10 --config=auto --output=semgrep-report.json --format=json /src || echo "Docker Semgrep failed"
                    else
                        echo "Docker not available"
                    fi
                    
                    # Попытка 2: Если Semgrep установлен
                    if command -v semgrep > /dev/null; then
                        semgrep --config=p/owasp-top-10 --config=auto --output=semgrep-report.json --format=json .
                    else
                        echo "Semgrep not installed"
                        touch semgrep-report.json
                    fi
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                echo 'SAST stage finished'
            }
        }
    }
}