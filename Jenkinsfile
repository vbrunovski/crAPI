pipeline {
    agent any
    
    stages {
        stage('SAST - Identity Service Only') {
            steps {
                script {
                    sh '''
                        echo "--- ДЕБАГ: Список файлов в services/identity ---"
                        ls -l "${WORKSPACE}/services/identity"
                        
                        echo "--- Запуск сканирования только identity ---"
                        # Запускаем docker, монтируем путь и просим сканировать /src/services/identity
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        returntocorp/semgrep \
                        semgrep scan \
                            --config auto \
                            --no-git-ignore \
                            --json \
                            /src/services/identity > "${WORKSPACE}/semgrep-report.json" || true
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
            }
        }
    }
}