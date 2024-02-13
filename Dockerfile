FROM apache/nifi:2.0.0-M2

ENV SINGLE_USER_CREDENTIALS_USERNAME=admin
ENV SINGLE_USER_CREDENTIALS_PASSWORD=nifi+langchain

COPY extensions/nifi-langchain-module/src/main/python/ /opt/nifi/nifi-current/python_extensions/

COPY extensions/nifi-langchain-helper/nifi-langchain-helper-nar/target/*.nar /opt/nifi/nifi-current/nar_extensions/

COPY data/samples/around-the-world-in-80-days-index /workspaces/nifi-langchain/data/samples/around-the-world-in-80-days-index

COPY examples /tmp/examples

COPY scripts/import.py /tmp/import.py

RUN python3 -m pip install requests

RUN /opt/nifi/scripts/start.sh > /dev/null 2>&1 & sleep 30 && python3 /tmp/import.py && /opt/nifi/nifi-current/bin/nifi.sh stop

RUN /opt/nifi/nifi-current/bin/nifi.sh start && sleep 60 && /opt/nifi/nifi-current/bin/nifi.sh stop

CMD /opt/nifi/nifi-current/bin/nifi.sh start && tail -f /opt/nifi/nifi-current/logs/nifi-app.log
