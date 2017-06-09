FROM jmfirth/webpack:wheezy

ENV NPM_CONFIG_LOGLEVEL warn
# 2: create directory:
RUN mkdir -p /frontend
COPY . /frontend

WORKDIR /frontend

RUN yarn
# 4: expose port

EXPOSE 8080

CMD ["yarn", "start"]