import json
import requests

from requests.auth import HTTPBasicAuth

from datadog import initialize, api
from datadog_checks.base import AgentCheck

__version__ = "1.0.0"


DATADOG_API_KEY = ''
USERNAME = ''
PASSWORD = ''
HOST = ''
PORT = ''

options = {'api_key': DATADOG_API_KEY}
initialize(**options)

def flatten_dict(prefix_str, input_dict):
    if prefix_str:
        prefix_str = prefix_str + '.'

    return_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            return_dict.update(
                flatten_dict(prefix_str + str(key), value)
            )
        elif isinstance(value, str):
            if str(value).strip().isdigit():
                return_value = int(value)
            else:
                continue
        elif isinstance(value, int):
            return_value = value
        else:
            raise ValueError("Unknown data type")

        return_key = prefix_str + str(key)
        return_dict[return_key] = return_value

    return return_dict

class PubSubCheck(AgentCheck):
    def check(self, instance):
        complete_stats_tuple_list = []

        # VPN LIST AND STATS
        msg_vpn_list = []
        response = requests.get(
            'http://{host}:{port}/SEMP/v2/monitor/msgVpns'.format(
                host=HOST, port=PORT
            ),
            auth=HTTPBasicAuth(USERNAME, PASSWORD)
        )

        response_obj = json.loads(response.content)
        for entry in response_obj.get('data', []):
            tags_list = ['vpn_name:{}'.format(entry['msgVpnName'])]
            stats_dict = flatten_dict('pubsub', entry)
            complete_stats_tuple_list.append((tags_list, stats_dict))
            msg_vpn_list.append(entry['msgVpnName'])

        # QUEUE LIST AND STATS
        msg_vpn_queue_dict = {}
        for msg_vpn in msg_vpn_list:
            response = requests.get(
                ('http://{host}:{port}/SEMP/v2/monitor/'
                 'msgVpns/{msg_vpn_name}/queues').format(
                     host=HOST, port=PORT, msg_vpn_name=msg_vpn
                 ),
                auth=HTTPBasicAuth(USERNAME, PASSWORD)
            )

            response_obj = json.loads(response.content)
            for entry in response_obj.get('data', []):
                tags_list = ['vpn_name:{}'.format(msg_vpn),
                             'queue_name:{}'.format(entry['queueName'])]
                stats_dict = flatten_dict('pubsub', entry)
                complete_stats_tuple_list.append((tags_list, stats_dict))
                if msg_vpn not in msg_vpn_queue_dict:
                    msg_vpn_queue_dict[msg_vpn] = []

                msg_vpn_queue_dict[msg_vpn].append(entry['queueName'])

        # BRIDGE LIST AND STATS
        msg_vpn_bridge_dict = {}
        for msg_vpn in msg_vpn_list:
            response = requests.get(
                ('http://{host}:{port}/SEMP/v2/monitor/msgVpns'
                 '/{msg_vpn_name}/bridges').format(
                     host=HOST, port=PORT, msg_vpn_name=msg_vpn
                 ),
                auth=HTTPBasicAuth(USERNAME, PASSWORD)
            )

            response_obj = json.loads(response.content)
            for entry in response_obj.get('data', []):
                tags_list = ['vpn_name:{}'.format(msg_vpn),
                             'bridge_name:{}'.format(entry['bridgeName'])]
                stats_dict = flatten_dict('pubsub', entry)
                complete_stats_tuple_list.append((tags_list, stats_dict))
                if msg_vpn not in msg_vpn_bridge_dict:
                    msg_vpn_bridge_dict[msg_vpn] = []

                msg_vpn_bridge_dict[msg_vpn].append(entry['bridgeName'])

        # QUEUE SUBSCRIPTIONS LIST AND STATS
        for msg_vpn, queue_list in msg_vpn_queue_dict.items():
            for queue_name in queue_list:
                response = requests.get(
                    ('http://{host}:{port}/SEMP/v2/monitor/msgVpns'
                     '/{msg_vpn_name}/queues/{queue_name}/'
                     'subscriptions').format(
                         host=HOST,
                         port=PORT,
                         msg_vpn_name=msg_vpn,
                         queue_name=queue_name
                     ),
                    auth=HTTPBasicAuth(USERNAME, PASSWORD)
                )

                response_obj = json.loads(response.content)
                for entry in response_obj.get('data', []):
                    tags_list = [
                        'vpn_name:{}'.format(msg_vpn),
                        'queue_name:{}'.format(queue_name),
                        'subscription_name:{}'.format(
                            entry['subscriptionTopic']
                        )
                    ]
                    stats_dict = flatten_dict('pubsub', entry)
                    complete_stats_tuple_list.append((tags_list, stats_dict))

        # TOPIC LIST AND STATS
        for msg_vpn in msg_vpn_list:
            response = requests.get(
                ('http://{host}:{port}/SEMP/v2/monitor/msgVpns'
                 '/{msg_vpn_name}/topicEndpoints').format(
                     host=HOST, port=PORT, msg_vpn_name=msg_vpn
                 ),
                auth=HTTPBasicAuth(USERNAME, PASSWORD)
            )

            response_obj = json.loads(response.content)
            for entry in response_obj.get('data', []):
                tags_list = ['vpn_name:{}'.format(msg_vpn),
                             'topic_endpoint_name:{}'.format(
                                 entry['topicEndpointName']
                             )]
                stats_dict = flatten_dict('pubsub', entry)
                complete_stats_tuple_list.append((tags_list, stats_dict))

        # TOPIC LIST AND STATS
        for msg_vpn in msg_vpn_list:
            response = requests.get(
                ('http://{host}:{port}/SEMP/v2/monitor'
                 '/msgVpns/{msg_vpn_name}/clients').format(
                     host=HOST, port=PORT, msg_vpn_name=msg_vpn
                 ),
                auth=HTTPBasicAuth(USERNAME, PASSWORD)
            )

            response_obj = json.loads(response.content)
            for entry in response_obj.get('data', []):
                tags_list = ['vpn_name:{}'.format(msg_vpn),
                             'client_name:{}'.format(
                                 entry['clientName'].strip('#')
                             )]
                stats_dict = flatten_dict('pubsub', entry)
                complete_stats_tuple_list.append((tags_list, stats_dict))

        # SEND METRICS TO DATADOG
        metric_dict_list = []
        for tag_list, metric_dict in complete_stats_tuple_list:
            for metric_name, metric_value in metric_dict.items():
                this_metric_dict = {}
                this_metric_dict['metric'] = metric_name
                this_metric_dict['points'] = metric_value
                this_metric_dict['tags'] = tag_list
                metric_dict_list.append(this_metric_dict)

        api.Metric.send(metric_dict_list)
