node("docker-builder") {
    stage('fetching'){
      checkout scm
    }
    stage('building'){
        try {
          sh 'docker-compose build --no-cache'
        } catch (e) {
          error 'building failed'
        } finally {
        }
    }
}

node("staging") {
    stage('testing'){
      try {
        sh 'docker-compose build --no-cache'
        sh 'docker-compose up'
      } catch (e) {
        error 'staging failed'
      } finally {
        //sh 'docker-compose down'
      }
    }
     stage('publish'){
        sh 'docker tag bigworldgraph 212.47.239.66:5000/bigworldgraph'
        sh 'docker push 212.47.239.66:5000/bigworldgraph'
    }
}

node("production-mobidick") {
    withEnv([
      "ENV=production"
    ]) {
      //sh 'docker service update --image  212.47.239.66:5000/bigworldgraph' bigworldgraph
    }
}