### Installation instructions
1. Copy pubsub.py into your Datadog agent's conf.d/ folder
2. Copy pubsub.yaml into your Datadog agetn's checks.d/ folder
3. Install the datadog Python library within your agent's pip namespace:

For Pivotal environments, run this command:

sudo LD_LIBRARY_PATH=/var/vcap/packages/dd-agent/embedded/lib /var/vcap/packages/dd-agent/embedded/bin/pip install datadog

For standard Linux environments, run this command:

sudo -Hu dd-agent /opt/datadog-agent/embedded/bin/pip install datadog

4. Restart the Datadog agent