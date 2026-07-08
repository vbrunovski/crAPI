pipeline {
    agent any

    stages {
        stage('SAST - Semgrep') {
            steps {
                script {
                    // Используем ${WORKSPACE} для корректного маппинга путей.
                    // Добавлена подкоманда 'scan' и аргумент '--json' согласно актуальным требованиям Semgrep.
                    sh '''
                        docker run --rm -v "${WORKSPACE}:/src" returntocorp/semgrep \
                        semgrep scan \
                            --config=p/owasp-top-10 \
                            --json \
                            --output=/src/semgrep-report.json \
                            /src
                    '''
                }
            }
        }

        stage('Archive Report') {
            steps {
                // Путь к файлу остается прежним, так как мы сохранили его в воркспейс
                archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                echo 'SAST report successfully archived.'
            }
        }
    }
}