#!groovy
@Library('Utilities') _

pipeline {
  agent { label 'clevercloud-node-builder' }

  environment {
    // Env
    PORT = 8080

    // Credentials
    BITBUCKET_CREDENTIALS = credentials('da3a4030-9e53-449b-9bed-82e4323fed67')
    CLEVER_TOKEN = credentials('cc_token')
    CLEVER_SECRET = credentials('cc_token_secret')

    // Deploy params
    DEPLOY_APP = getDeployApp()
  }

  options {
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '15'))
    ansiColor('xterm')
    timeout(time: 30, unit: 'MINUTES')
  }

  triggers {
    pollSCM('')
  }

  stages {
    stage('Checkout') {
      steps {
        slackNotify()
      }
    }

    stage('Build') {
      steps {
        dir("frontend") {
          sh "clever env -a $DEPLOY_APP > .env"
          sh "npm ci"
          sh "npm run build"
        }
      }
    }

    stage('Run') {
      steps {
        dir("frontend") {
          sh "npm start &"
        }
      }
    }

    stage('Test') {
      steps {
        timeout(5) {
          waitUntil {
            script {
              testCurl("localhost:${PORT}")
            }
          }
        }
      }
    }

    stage('Deploy') {
      when {
        expression {
          return isProduction() || isStaging()
        }
      }

      steps {
        script {
          dir("frontend") {
            echo("Deploying to $DEPLOY_APP")
            sh "pwd"
            sh "ls -alh"
            sh "cat .clever.json"
            sh "clever deploy -a $DEPLOY_APP -f"
            echo("Project available on $DEPLOY_APP")
          }
        }
      }
    }
  }

  post {
    always {
      echo 'Run regardless of the completion status of the Pipeline run.'
      script {
        slackNotify(currentBuild.result)
      }
    }
    changed {
      echo 'Only run if the current Pipeline run has a different status from the previously completed Pipeline.'
    }
    success {
      echo 'Only run if the current Pipeline has a "success" status, typically denoted in the web UI with a blue or green indication.'
    }
    failure {
      echo 'Only run if the current Pipeline has a "failure" status, usually caused by errors in jenkinsfile, etc. Typically denoted in the web UI with a red indication.'
    }
    unstable {
      echo 'Only run if the current Pipeline has an "unstable" status, usually caused by test failures, code violations, etc. Typically denoted in the web UI with a yellow indication.'
    }
    aborted {
      echo 'Only run if the current Pipeline has an "aborted" status, usually due to the Pipeline being manually aborted. Typically denoted in the web UI with a gray indication.'
    }
  }
}

def isStaging() {
  return BRANCH_NAME == 'develop'
}

def isProduction() {
  return BRANCH_NAME == 'master'
}

def getDeployApp() {
  if (isProduction()) {
    return 'production'
  }
  return 'staging'
}
