from a2ml.api.base_a2ml import BaseA2ML
from a2ml.api.utils.show_result import show_result


class A2ML(BaseA2ML):
    """Facade to A2ML providers."""

    def __init__(self, ctx, provider = None):
        """Initializes A2ML PREDIT instance.

        Args:
            context (object): An instance of the a2ml Context.
            provider (str): The automl provider(s) you wish to run. For example 'auger,azure,google'.
        
        Returns:
            A2ML object

        Examples:
            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
        """
        super(A2ML, self).__init__()
        self.ctx = ctx
        self.runner = self.build_runner(ctx, provider)
        self.local_runner = lambda: self.build_runner(ctx, provider, force_local=True)

    @show_result
    def import_data(self, source=None):
        """Imports data defined in context. Uploading the same file name will result in versions being appended to the file name.

        Note:
            Your context points to a config file where ``source`` is defined.

            .. code-block:: yaml

                # Local file name or remote url to the data source file
                source: './dataset.csv'
        
        Args:
            source (str, optional): Local file name or remote url to the data source file

        Returns:
            Results for each provider. ::

                {
                    'auger': {'result': True, 'data': {'created': 'dataset.csv'}}, \n
                    'azure': {'result': True, 'data': {'created': 'dataset.csv'}}
                }
            
            Failures will return error messages. ::

                {
                    'auger': {'result': False, 'data': 'Please specify data source file...'}, \n
                    'azure': {'result': False, 'data': 'Please specify data source file...'}
                }

        
            
        Examples:
            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
                a2ml.import_data()
        """
        return self.runner.execute('import_data', source=source)

    @show_result
    def train(self):
        """Starts training session based on context state.

        Returns:
            Results for each provider. ::

                {
                    'auger': {
                        'result': True,
                        'data': {
                            'eperiment_name': 'dataset.csv-4-experiment',
                            'session_id': '9ccfe04eca67757a'
                         }
                    }
                }

            Failures will return error messages. ::

                {
                    'auger': {'result': False, 'data': 'Please set target to build model.'}
                }

        Examples:

            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
                a2ml.train()

        """
        return self.runner.execute('train')

    @show_result
    def evaluate(self, run_id = None):
        """Evaluate the results of training.
        
        Args:
            run_id (str, optional): The run id for a training session. A unique run id is created for every train. Default is last experiment train.
            
        Returns:
            Results for each provider. ::

                {
                    'auger': {
                        'result': True,
                        'data': {
                            'run_id': '9ccfe04eca67757a',
                            'leaderboard': [
                                {'model id': 'A017AC8EAD094FD', 'rmse': '0.0000', 'algorithm': 'LGBMRegressor'},
                                {'model id': '4602AFCEEEAE413', 'rmse': '0.0000', 'algorithm': 'ExtraTreesRegressor'}
                            ],
                            'status': 'started'
                        }
                    }
                }

            **Status**

                * **preprocess** - search is preprocessing data for traing
                * **started** - search is in progress
                * **completed** - search is completed
                * **interrupted** - search was interrupted

            Examples:
                .. code-block:: python

                    ctx = Context()
                    a2ml = A2ML(ctx, 'auger, azure')
                    while True:
                        res = a2ml.evaluate()
                        if status['auger']['status'] not in ['preprocess','started']:
                            break
        """
        return self.runner.execute('evaluate', run_id = run_id)

    @show_result
    def deploy(self, model_id, locally=False, review=True):
        """Deploy a model locally or to specified provider(s).

        Note:
            See evaluate function to get model_id

        Args:
            model_id (str): The model id from any experiment you will deploy
            locally(bool): Deploys the model locally if True, on the Provider Cloud if False. The default is False.
            review(bool): Should model support review based on actual data. The default is True.
        
        Returns:
            Results for each provider. ::

                {
                    'auger': {
                        'result': True,
                        'data': {'model_id': 'A017AC8EAD094FD'}
                    }
                }

        Examples:
            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
                a2ml.deploy(model_id='A017AC8EAD094FD')
        """
        return self.__get_runner(locally).execute('deploy', model_id, locally, review)

    @show_result
    def predict(self, filename, model_id, threshold=None, locally=False, data=None, columns=None, output=None):
        """Predict results with new data against deployed model. Predictions are stored next to the file with data to be predicted on. The file name will be appended with suffix _predicted.

        Args:
            filename(str, optional): The file with data to request predictions for. Data param is not passed in this case.
            data(list, optional): The list of records to get predictions for. Filename param is not passed in this case.
            model_id(str): The deployed model id you want to use.
            threshold(float, optional): For classification models only. This will return class probabilities with response.
            locally(bool, optional): Predicts using a local model if True, on the Provider Cloud if False. The default is False.
            output(str): Output csv file path.

        Results:
            Results for each provider. ::

                {
                    'auger': {
                        'result': True,
                        'data': {'predicted': '<path_to_file>/dataset_predicted.csv'}
                        }
                    }
                }

        Examples:
            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
                a2ml.predict(model_id='D881079E1ED14FB',filename=<path_to_file>/dataset.csv)

            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
                data = [{'col1': 'value1', 'col2': 'value2'}, {'col1': 'value3', 'col2': 'value4'}]
                a2ml.predict(model_id='D881079E1ED14FB',data=data)

            .. code-block:: python

                ctx = Context()
                a2ml = A2ML(ctx, 'auger, azure')
                data = [[value1, value2], [value3, value4]]
                columns = [col1, col2]
                a2ml.predict(model_id='D881079E1ED14FB',data=data,columns=columns)
                
           
        """
        return self.__get_runner(locally).execute('predict', filename, model_id, threshold, locally, data, columns, output)

    @show_result
    def review(self):
        """Review the performance of deployed model."""
        return self.runner.execute('review')

    def __get_runner(self, locally):
        if locally:
            return self.local_runner()
        else:
            return self.runner
