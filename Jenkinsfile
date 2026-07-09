pipeline {
    agent any
    stages {
        stage('Where is my code?') {
            steps {
                script {
                    // Эта команда покажет всю структуру папок внутри Jenkins
                    sh 'ls -R "${WORKSPACE}"'
                }
            }
        }
    }
}