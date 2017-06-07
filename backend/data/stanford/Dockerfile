FROM openjdk:9-jre
MAINTAINER Kaleidophon (https://github.com/Kaleidophon)

RUN mkdir /stanford_models/
WORKDIR /stanford_models/

RUN export CLASSPATH="`find . -name '*.jar'`"

EXPOSE 9000

CMD java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout \
15000 -serverProperties StanfordCoreNLP-french.properties
