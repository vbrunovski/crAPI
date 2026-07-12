pipeline {
    agent any
    
    stages {
        stage('SAST - Identity Service Only') {
            steps {
                script {
                    // Мы сканируем файлы текущей директории Jenkins и передаем их в контейнер через tar
                    // Это обходит все проблемы с маунтами
                    sh '''
                        echo "--- Сканирование через передачу архива ---"
                        tar -cf - services/identity | docker run --rm -i -v /src returntocorp/semgrep sh -c "tar -xf - && semgrep scan --config auto --no-git-ignore --json services/identity" > "${WORKSPACE}/semgrep-report.json"
                    '''
                }
            }
        }

        stage('DAST Scan (Nuclei)') {
    steps {
        script {
            sh '''
            echo "--- Запуск Nuclei ---"
            # Запускаем и перенаправляем stderr в stdout, чтобы видеть ошибки в консоли Jenkins
            docker run --rm -v "${WORKSPACE}:/output" projectdiscovery/nuclei:latest \
                -target http://localhost:8080 \
                -severity medium,high,critical \
                -o /output/nuclei_report.txt 2>&1
            
            echo "--- Проверка наличия файла ---"
            # Обязательно используем кавычки вокруг переменной с пробелом
            if [ -f "${WORKSPACE}/nuclei_report.txt" ]; then
                echo "Файл успешно создан!"
                ls -la "${WORKSPACE}/nuclei_report.txt"
            else
                echo "ФАЙЛ НЕ СОЗДАН!"
                # Выведем содержимое папки, чтобы увидеть, где он мог оказаться
                ls -la "${WORKSPACE}"
            fi
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
}