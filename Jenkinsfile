node("docker-builder") {
    commitChangeset = sh(returnStdout: true, script: 'git log --oneline -n 1').trim()
    slackSend color: '#0066cc', message: "Starting to build BigWorldGraph! :muscle: ( ${commitChangeset} )"

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
    commitChangeset = sh(returnStdout: true, script: 'git log --oneline -n 1').trim()
    stage('fetching'){
        checkout scm
    }
    stage('testing'){
        slackSend color: '#993366', message: "Starting to test BigWorldGraph... :alembic::bar_chart::mag: ( ${commitChangeset} )"
        try {
            sh 'docker-compose -f docker-compose-test.yml build --no-cache'
            sh 'docker-compose -f docker-compose-test.yml up & \
                while :; do \
                    if [[ $(docker logs --since 2s bigworldgraphr3_backend_1 2>&1 | grep "OK") ]]; \
                    then \
                        docker kill bigworldgraphr3_neo4j_1; \
                        break; \
                    elif [[ $(docker logs --since 2s bigworldgraphr3_backend_1 2>&1 | grep -o "FAILED") ]]; \
                    then \
                        docker kill bigworldgraphr3_neo4j_1; \
                        exit 1; \
                    fi; \
                    sleep 1; \
                done;' \
        } catch (e) {
            error 'staging failed'
            slackSend color: 'danger', message: 'BigWorldGraph tests failed :cry:'
        } finally {
            slackSend color: '#993366', message: "Testing BigWorldGraph was successful! :nerd_face::+1: ( ${commitChangeset} )"
        }
    }
    stage('publish'){
        sh 'docker tag bigworldgraph_backend 212.47.239.66:5000/bigworldgraph_backend'
        sh 'docker push 212.47.239.66:5000/bigworldgraph_backend'

        sh 'docker tag bigworldgraph_frontend 212.47.239.66:5000/bigworldgraph_frontend'
        sh 'docker push 212.47.239.66:5000/bigworldgraph_frontend'
    }
}

node("production-mobidick") {
    commitChangeset = sh(returnStdout: true, script: 'git log --oneline -n 1').trim()
    stage('staging_fetching'){
        checkout scm
    }

    stage('staging_deploy') {
        sh 'docker stack deploy --compose-file docker-compose-production.yml bigworldgraph'
        slackSend color: 'good', message: "BigWorldGraph build successful! :triumph: ( ${commitChangeset} )"
    }
}