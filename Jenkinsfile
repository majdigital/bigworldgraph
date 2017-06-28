node("docker-builder") {
    stage('fetching'){
      checkout bigworldgraph
    }
    stage('building'){
        try {
          sh 'docker-compose build --no-cache -t bigworldgraph'
          sh 'docker-compose up'
        } catch (e) {
          error 'building failed'
        } finally {
          sh 'docker-compose down'
        }
    }
}

node("docker-testin") {
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
        sh 'docker tag bigworldgraph 10.2.74.19:5000/bigworldgraph'
        sh 'docker push 10.2.74.19:5000/bigworldgraph'
    }
}

node("docker-production") {
    withEnv([
      "ENV=production"
    ]) {
      //sh 'docker service update --image  10.2.74.19:5000/bigworldgraph' bigworldgraph
    }
}