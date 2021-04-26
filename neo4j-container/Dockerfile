FROM neo4j:4.1.4

ENV APOC_VERSION=4.1.0.0

ENV APOC_URI=https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/${APOC_VERSION}/apoc-${APOC_VERSION}-all.jar

ENV GRAPHQL_VERSION=3.5.21.5
ENV GRAPHQL_URI=https://github.com/neo4j-graphql/neo4j-graphql/releases/download/${GRAPHQL_VERSION}/neo4j-graphql-${GRAPHQL_VERSION}.jar

ADD --chown=neo4j:neo4j ${APOC_URI} plugins
ADD --chown=neo4j:neo4j ${GRAPHQL_URI} plugins

ENV NEO4J_dbms_unmanaged__extension__classes=org.neo4j.graphql=/graphql

USER root

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    curl \
    python3.5 \
    python3-pip \
    python3-setuptools \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install wheel

RUN pip3 install awscli

USER neo4j

COPY parse_data.py parse_data.py

COPY import.sh import.sh

ENV EXTENSION_SCRIPT=import.sh

ENV NEO4J_dbms_default__database=discover.db

NEO4J_browser_allow__outgoing__connections

CMD [ "neo4j" ]
