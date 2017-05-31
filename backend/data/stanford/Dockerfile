FROM openjdk:9-jre
MAINTAINER Kaleidophon (https://github.com/Kaleidophon)

RUN mkdir /stanford_models/
#RUN if [ ! -f /stanford_models/UD_French.gz ]; then wget majconsulting.ch/newsletters/stanford_models_french_100417.zip -P /stanford_models/; fi
#RUN apt-get update
#RUN apt-get install -y zip
#RUN if [ -f /stanford_models/stanford_models_french_100417.zip ]; then unzip /stanford_models/stanford_models_french_100417.zip -d /stanford_models/ && rm /stanford_models/stanford_models_french_100417.zip; fi
RUN echo test >> /stanford_models/test.txt

WORKDIR /stanford_models/

RUN export CLASSPATH="`find . -name '*.jar'`"

EXPOSE 9000

CMD java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout \
15000 -serverProperties StanfordCoreNLP-french.properties
