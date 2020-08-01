pipeline {
  agent {
    label 'slave'
  }

  options {
    ansiColor('xterm')
    timeout(time: 1, unit: 'HOURS')
    timestamps()
  }

  stages {
    stage('check-gh-trust') {
      steps {
        checkGitHubAccess()
      }
    }

    stage('test') {
      steps {
        sh 'make test'
      }
    }
  }

  post {
    failure {
      emailNotification()
    }
    always {
      ircNotification()
    }
  }
}

// vim: ft=groovy
