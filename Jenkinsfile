pipeline {
    agent any
    
    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    def semgrep = docker.image('returntocorp/semgrep')
                    semgrep.inside('-u root') {
                        sh '''
                            semgrep --config=p/owasp-top-10 \
                                    --config=auto \
                                    --output=semgrep-report.json \
                                    --format=json \
                                    .
                        '''
                    }
                }
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
            }
        }
    }
}