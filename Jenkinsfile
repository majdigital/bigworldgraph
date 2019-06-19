#!groovy

DEPLOY_URL_STAGING = 'bigworldgraph-stage.maj.digital'
DEPLOY_URL_PRODUCTION = 'bigworldgraph.maj.digital'

pipeline {
  agent any

  environment {
    // Project variables
    REPO = 'bigworldgraph'
    COMPOSE_PROJECT_NAME = 'bigworldgraph'
    // TODO: multiple ports?
    PORT = 8080

    // Build params
    BUILD_TYPE_PROD = 'production'
    BUILD_TYPE_DEV = 'staging'
    BUILD_TYPE = getBuildType()
    BUILD_TAG = getTag()

    // AWS
    AWS_REGION = 'eu-central-1'
    ECR_URL = "894738297687.dkr.ecr.${AWS_REGION}.amazonaws.com/majdigital/"
    IP_MANAGER_SWARM = getIpManagerSwarm()

    DEPLOY_URL = getDeployUrl()
  }

  options {
    disableConcurrentBuilds()
    buildsDiscarder(logRotator(numToKeepStr: '15'))
    ansiColor('xterm')
    timeout(time: 15, unit: 'MINUTES')
  }

  triggers {
    pollSCM('')
  }

  stages {
    stage('Checkout') {
      when {
        expression {
          return isProduction() || isStaging()
        }
      }

      steps {
        slackNotify()
      }
    }

    stage('Build') {
      when {
        expression {
          return isProduction() || isStaging()
        }
      }

      steps {
        echo '##### Start Build #####'

        // TODO: create env files
        // sh "cp .env.$BUILD_TYPE .env"

        // Clean Docker from previous Jenkins Jobs
        sh "docker system prune -a -f --volumes"

        // Build image, here only express
        // TODO: check this
        sh "docker-compose -f docker/docker-compose-CI.yml build"
      }

      post {
        success {
          echo "##### Tag for private registry on AWS ECR #####"
          // TODO: check if there's any other images to tag
          sh "docker tag majdigital/${COMPOSE_PROJECT_NAME}_frontend ${ECR_URL}${REPO}_frontend:${BUILD_TAG}"
        }
      }
    }

    stage('Run') {
      when {
        expression {
          return isProduction() || isStaging()
        }
      }

      steps {
        // Start application serivces (-d: run in background)
        // TODO: check this
        sh "docker-compose -f docker/docker-compose-CI.yml up -d"
        sleep 15
        sh "docker ps -a"
      }
    }

    stage('Test') {
      when {
        expression {
          return isProduction() || isStaging()
        }
      }

      steps {
        // Logs output
        echo "##### Logs of services #####"
        sh "docker network ls"
        sh "docker volume ls"
        sh "docker ps -a"

        // Waiting app to be ready (log like 'Listening on http://172.18.0.2:3000')
        // TODO: create service 'frontend'
        sh """
          while ! docker logs ${COMPOSE_PROJECT_NAME}_frontend | grep 'Project is running at http://0.0.0.0:${PORT}/'
              do sleep 10
          done
        """

        // Logs of containers
        sh "docker logs ${COMPOSE_PROJECT_NAME}_frontend"

        // Inspect docker containers
        sh "docker inspect ${COMPOSE_PROJECT_NAME}_frontend"

        echo "##### Test of services #####"

        // TODO: DO SOMETHING ELSE?

        // External access
        sh "curl -I http://localhost:${PORT}"
      }

      post {
        always {
          echo "##### Remove stack #####"
          sh "docker-compose -f docker/docker-compose-CI.yml down"
          sleep 10
        }

        success {
          echo "##### Push image to AWS ECR Docker repository #####"
          echo "Built image will be available at: '${ECR_URL}${REPO}_frontend:${BUILD_TAG}'"

          script {
            // Getting token and login for AWS ECR registry
            sh "\$(aws ecr get-login --region $AWS_REGION | sed -e 's/-e none//g')"

            // Create repository if no exists
            // TODO: check if there's any other images to upload
            sh """
              if ! aws ecr describe-repositories --region $AWS_REGION --repository-names majdigital/${REPO}_frontend
              then
                echo 'No ECR repository!'
                aws ecr create-repository --region $AWS_REGION --repository-name majdigital/${REPO}_frontend
              fi
              docker push ${ECR_URL}${REPO}_frontend:${BUILD_TAG}
            """
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
        echo "##### Start deploying #####"

        script {
          echo("Deploying to $BUILD_TYPE")
          // TODO: handle the DB
          // echo "Display folders available on EFS file system - /efs/ SWARM CLUSTER:"
          // sshagent(credentials: ['ssh-ec2']) {
          //   // Display all folders on EFS file system
          //   sh "ssh -o StrictHostKeyChecking=no admin@$IP_MANAGER_SWARM ls -al /efs"
          //   sh "ssh -o StrictHostKeyChecking=no admin@$IP_MANAGER_SWARM sudo mkdir -p /efs/$BUILD_TYPE/${COMPOSE_PROJECT_NAME}_db"
          // }

          sh """
            docker -H $IP_MANAGER_SWARM:2375 stack rm $REPO
            docker -H $IP_MANAGER_SWARM:2375 service ls
            docker -H $IP_MANAGER_SWARM:2375 stack deploy -c docker/docker-compose-deploy.yml $REPO --with-registry-auth
            sleep 5
            docker -H $IP_MANAGER_SWARM:2375 stack ls
            docker -H $IP_MANAGER_SWARM:2375 service ls
            sleep 10
            docker -H $IP_MANAGER_SWARM:2375 stack ps $REPO
          """
          echo("Project available on $DEPLOY_URL")
        }
      }
    }
  }

  post {
    always {
      echo 'Run regardless of the completion status of the Pipeline run.'
    }
    changed {
      echo 'Only run if the current Pipeline run has a different status from the previously completed Pipeline.'
    }
    success {
      echo 'Only run if the current Pipeline has a "success" status, typically denoted in the web UI with a blue or green indication.'
      script {
        if (isProduction() || isStaging()) {
          slackNotify(currentBuild.result)
        }
      }
    }
    failure {
      script {
        if (isProduction() || isStaging()) {
          slackNotify(currentBuild.result)
        }
      }
    }
    unstable {
      echo 'Only run if the current Pipeline has an "unstable" status, usually caused by test failures, code violations, etc. Typically denoted in the web UI with a yellow indication.'
      script {
        if (isProduction() || isStaging()) {
          slackNotify(currentBuild.result)
        }
      }
    }
    aborted {
      echo 'Only run if the current Pipeline has an "aborted" status, usually due to the Pipeline being manually aborted. Typically denoted in the web UI with a gray indication.'
      script {
        if (isProduction() || isStaging()) {
          slackNotify(currentBuild.result)
        }
      }
    }
  }
}

def isStaging() {
  return BRANCH_NAME == 'develop'
}

def isProduction() {
  return BRANCH_NAME == 'master'
}

def getBuildType() {
  if (isStaging()) {
    return 'staging'
  }
  if (isProduction()) {
    return 'production'
  }
  return null
}

def getTag() {
  if (isStaging()) {
    return 'staging'
  }
  if (isProduction()) {
    return 'lastest'
  }
  return null
}

def getIpManagerSwarm() {
  def type = getBuildType()

  if (type == null) return null

  def manager = [
    name: type == 'production' ? 'SwarmManager-PROD' : 'SwarmManager-staging',
    region: 'eu-central-1'
  ]

  def command = "aws ec2 describe-instances --region $manager.region --filters 'Name=tag:Name,Values=$manager.name' --query 'Reservations[].Instances[].PrivateIpAddress' --output text"

  def output = sh(returnStdout: true, script: command)

  return type == 'production' ? output.tokenize()[1].trim() : output.trim()
}

def getDeployUrl() {
  if (isStaging()) {
    return DEPLOY_URL_STAGING
  }
  if (isProduction()) {
    return DEPLOY_URL_PRODUCTION
  }
  return null
}

def slackNotify(String buildStatus = 'STARTED') {
  // Build status of null means success.
  buildStatus = buildStatus ?: 'SUCCESS'

  if (buildStatus == 'STARTED') {
    colorCode = '#FFDE3A'
  } else if (buildStatus == 'SUCCESS') {
    colorCode = '#1ED761'
  } else if (buildStatus == 'UNSTABLE') {
    color = '#FF7E04'
  } else {
    colorCode = '#EB3831'
  }

  // def msg = "${buildStatus}: `${env.JOB_NAME}` #${env.BUILD_NUMBER}:\n${env.BUILD_URL}"
  def msg = "Here is the env: ${env}"

  slackSend(color: colorCode, message: msg)
}
