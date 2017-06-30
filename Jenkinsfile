// Test comment

node("docker-builder") {
    stage('fetching'){
        checkout scm
    }
    stage('building'){
        try {
            sh 'docker-compose build --no-cache'
        } catch (e) {
            error 'building failed'
        } finally {}
    }
}

node("staging") {
    stage('fetching'){
        checkout scm
    }
    stage('testing'){
        try {
            sh 'docker-compose -f docker-compose-test.yml build --no-cache'
            sh 'docker-compose -f docker-compose-test.yml up'
            sh 'while :; do \
                if  [ $(docker logs bigworldgraphr3_backend_1 2>&1 | grep "OK" | wc -l) > 1 ]; \
                then \
                    docker kill bigworldgraphr3_neo4j_1; \
                    docker kill bigworldgraphr3_backend_1; \
                    break; \
                elif [ $(docker logs bigworldgraphr3_backend_1 2>&1 | grep "FAILED" | wc -l) > 1 ]; \
                then \
                    exit 1; \
                fi; \
                done'
        } catch (e) {
            error 'staging failed'
        } finally {
            //sh 'docker kill bigworldgraphr3_neo4j_1'
            //sh 'docker kill bigworldgraphr3_backend_1'
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