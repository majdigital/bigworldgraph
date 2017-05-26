FROM node:latest

ENV NPM_CONFIG_LOGLEVEL warn
# 2: create directory:
RUN mkdir -p /frontend
COPY . /frontend
RUN npm install -gq gulp

WORKDIR /frontend


RUN npm i gulp
# 4: expose port

EXPOSE 8080
CMD ["gulp"]
