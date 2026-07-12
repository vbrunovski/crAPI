pipeline {
    agent any
    
    stages {
        stage('SAST - Identity Service') {
            steps {
                script {
                    sh 'tar -cf - services/identity | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config auto --no-git-ignore --json services/identity" > "${WORKSPACE}/semgrep-report.json"'
                }
            }
        }

        stage('Deploy App Test Стенд') {
            steps {
                script {
                    echo "--- Сборка и развертывание crAPI из исходного кода репозитория ---"
                    
                    // Переходим в папку deploy и запускаем сборку через локальный docker-compose хоста, 
                    // передавая файл через стандартный ввод, чтобы обойти баги старых версий docker cli
                    sh '''
                        cd deploy
                        docker compose up -d --build
                    '''
                    
                    echo "--- Ожидание инициализации сервисов ---"
                    sh 'sleep 60' // Даем чуть больше времени, так как сервисы будут собираться
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
            steps {
                script {
                    echo "--- Запуск Nuclei против поднятого локально crAPI ---"
                    // В стандартном docker-compose.yml crAPI вешается на порт 8888 хоста.
                    // Запускаем Nuclei в режиме хост-сети, чтобы он достучался до 8888 порта.
                    sh '''
                    docker run --rm --network host -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest \
                        -target http://localhost:8888 \
                        -severity medium,high,critical \
                        -o /output/nuclei_report.txt -v
                    '''
                }
            }
        }
        
        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'semgrep-report.json, nuclei_report.txt', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo 'Очистка тестового стенда...'
            sh '''
                cd deploy
                docker compose down
            '''
        }
    }
}