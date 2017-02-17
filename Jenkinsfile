node('slave') {
    step([$class: 'WsCleanup'])

    stage('check-out-code') {
        checkout scm
    }

    stage('test') {
        sh 'make test'
    }
}

// vim: ft=groovy
