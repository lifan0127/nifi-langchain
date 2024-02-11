#!/bin/bash

nifi_logs_dir=/opt/nifi/nifi-current/logs

tail -f ${nifi_logs_dir}/nifi-app.log -f ${nifi_logs_dir}/nifi-python.log