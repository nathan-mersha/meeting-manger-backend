pipeline {
    agent any
    stages {

        stage('Build') {
            steps {
                sh "pip3 install -r requirements.txt"
            }
        }

        stage('Kill previous') {
            steps {
                sh "killall gunicorn -q | echo 'no process found'"
            }
        }

        stage('Deploy') {
            steps {
                sh "gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind '0.0.0.0:8000' --daemon"
            }
        }

    }
}