from a2ml.tasks_queue.tasks_hub_api import *


class TestTasksHubApiAuger(object):

    @pytest.mark.skip(reason='run it locally')
    def test_evaluate_start(self):
        params = {
            'provider': "azure",
            'augerInfo': {
                'experiment_session_id': '010def8e3cb89236'
            },
            'provider_info': {
                'auger': {
                    'credentials': {
                        "url": "https://app-staging.auger.ai",
                        "token": "XXX",
                        "organization": "mt-org"
                    }
                },
                'azure' : {
                    'credentials': {
                        "subscription_id":"XXX",
                        "directory_tenant_id":"XXX",
                        "application_client_id":"XXX",
                        "client_secret":"XXX"
                    },
                    'dataset': 'adult-822d0fbc.data.csv',
                    'project':{
                        'name': 'a2ml_azure_adult_3'
                    },
                    'experiment': {
                        'name': 'adult-data-csv',
                    },
                    'cluster': {
                        'name': 'cpucluster',
                        'min_nodes': 0,
                        'max_nodes': 2,
                        'type': 'STANDARD_D2_V2'
                    }
                }
            }
        }
        res = evaluate_start_task(params)
        print(res)
