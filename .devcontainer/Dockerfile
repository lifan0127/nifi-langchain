FROM apache/nifi:2.0.0-M2

USER root

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install Maven
RUN curl -O https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz \
  && tar -xzf apache-maven-3.9.6-bin.tar.gz -C /opt/ \
  && rm apache-maven-3.9.6-bin.tar.gz

USER nifi