### Installation instructions
1. Copy pubsub.py into your Datadog agent's conf.d/ folder
2. Edit pubsub.py to provide your Datadog API key as well as your Solace SEMP API username, password, host, and port
3. Copy pubsub.yaml into your Datadog agetn's checks.d/ folder
4. Install the datadog Python library within your agent's pip namespace:

For Pivotal environments, run this command:

`sudo LD_LIBRARY_PATH=/var/vcap/packages/dd-agent/embedded/lib /var/vcap/packages/dd-agent/embedded/bin/pip install datadog`

For standard Linux environments, run this command:

`sudo -Hu dd-agent /opt/datadog-agent/embedded/bin/pip install datadog`

5. Restart the Datadog agent
