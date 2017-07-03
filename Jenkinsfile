// Test comment

node("docker-builder") {
//    stage('fetching'){
//        checkout scm
//    }
//    stage('building'){
//        try {
//            sh 'docker-compose build --no-cache'
//        } catch (e) {
//            error 'building failed'
//        } finally {}
//    }
}

node("staging") {
    stage('fetching'){
        checkout scm
    }
    stage('testing'){
        withEnv([
            "NEO4J_PASSWORD_TEST=1234"
        ]) {
            sh 'echo password ${NEO4J_PASSWORD_TEST}'
            try {
                sh 'docker-compose -f docker-compose-test.yml build --no-cache'
                sh 'docker-compose -f docker-compose-test.yml up & \
                    while :; do \
                        echo Checking; \
                        if [[ $(docker logs --since 1s bigworldgraphr3_backend_1 2>&1 | grep "OK") ]]; \
                        then \
                            echo Testing okay; \
                            docker kill bigworldgraphr3_neo4j_1; \
                            break; \
                        elif [[ $(docker logs --since 2s bigworldgraphr3_backend_1 2>&1 | grep "FAILED") ]]; \
                        then \
                            echo Testing looks bad; \
                            docker kill bigworldgraphr3_neo4j_1; \
                            exit 1; \
                        fi; \
                        sleep 1; \
                    done;' \
            } catch (e) {
                error 'staging failed'
            } finally {}
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