import os
import shutil
import subprocess
from zipfile import ZipFile

from .deploy import ModelDeploy
from ..cloud.cluster import AugerClusterApi
from ..cloud.pipeline import AugerPipelineApi
from ..exceptions import AugerException
from a2ml.api.utils import fsclient
from a2ml.api.utils.dataframe import DataFrame
from a2ml.api.model_review.model_helper import ModelHelper

class ModelPredict():
    """Predict using deployed Auger Model."""

    def __init__(self, ctx):
        super(ModelPredict, self).__init__()
        self.ctx = ctx

    def execute(self, filename, model_id, threshold=None, locally=False, data=None, columns=None, output=None):
        if filename and not fsclient.is_s3_path(filename):
            self.ctx.log('Predicting on data in %s' % filename)
            filename = os.path.abspath(filename)

        if locally:
            predicted = self._predict_locally(filename, model_id, threshold, data, columns, output)
        else:
            predicted = self._predict_on_cloud(filename, model_id, threshold, data, columns, output)

        return predicted

    def _predict_on_cloud(self, filename, model_id, threshold, data, columns, output):
        ds = DataFrame.create_dataframe(filename, data, columns)

        pipeline_api = AugerPipelineApi(self.ctx, None, model_id)
        predictions = pipeline_api.predict(ds.get_records(), ds.columns, threshold)

        ds_result = DataFrame.create_dataframe(None, records=predictions['data'], features=predictions['columns'])
        ds_result.options['data_path'] = filename
        ds_result.loaded_columns = columns
        return ModelHelper.save_prediction_result(ds_result, 
            prediction_id = None, support_review_model = False, 
            json_result=False, count_in_result=False, prediction_date=None, 
            model_path=None, model_id=model_id, output=output)

    def _predict_locally(self, filename_arg, model_id, threshold, data, columns, output):
        model_deploy = ModelDeploy(self.ctx, None)
        is_model_loaded, model_path, model_name = \
            model_deploy.verify_local_model(model_id)

        if not is_model_loaded:
            raise AugerException('Model isn\'t loaded locally. '
                'Please use a2ml deploy command to download model.')

        model_path, model_existed = self._extract_model(model_name)
        model_options = fsclient.read_json_file(os.path.join(model_path, "model", "options.json"))

        filename = filename_arg
        if not filename:
            ds = DataFrame.create_dataframe(filename, data, columns)            
            filename = os.path.join(self.ctx.config.get_path(), '.augerml', 'predict_data.csv')
            ds.saveToCsvFile(filename, compression=None)

        try:
            predicted = \
                self._docker_run_predict(filename, threshold, model_path)
        finally:
            # clean up unzipped model
            # if it wasn't unzipped before
            if not model_existed:
                shutil.rmtree(model_path, ignore_errors=True)
                model_path = None

        if not filename_arg:
            ds_result = DataFrame.create_dataframe(predicted)

            ds_result.options['data_path'] = None
            ds_result.loaded_columns = columns

            return ModelHelper.save_prediction_result(ds_result, 
                prediction_id = None, 
                support_review_model = model_options.get("support_review_model") if model_path else False, 
                json_result=False, count_in_result=False, prediction_date=None, 
                model_path=model_path, model_id=model_id, output=output)
        elif output:
            fsclient.move_file(predicted, output)
            predicted = output

        return predicted
            
    def _extract_model(self, model_name):
        model_path = os.path.splitext(model_name)[0]
        model_existed = os.path.exists(model_path)

        if not model_existed:
            with ZipFile(model_name, 'r') as zip_file:
                zip_file.extractall(model_path)

        return model_path, model_existed

    def _docker_run_predict(self, filename, threshold, model_path):
        cluster_settings = AugerClusterApi.get_cluster_settings(self.ctx)
        docker_tag = cluster_settings.get('kubernetes_stack')
        predict_file = os.path.basename(filename)
        data_path = os.path.abspath(os.path.dirname(filename))
        model_path = os.path.abspath(model_path)

        call_args = "--verbose=True --path_to_predict=./model_data/%s %s" % \
            (predict_file, "--threshold=%s" % str(threshold) if threshold else '')

        command = (r"docker run "
            "-v {model_path}:/var/src/auger-ml-worker/exported_model "
            "-v {data_path}:/var/src/auger-ml-worker/model_data "
            "deeplearninc/auger-ml-worker:{docker_tag} "
            "python ./exported_model/client.py {call_args}").format(
                model_path=model_path, data_path=data_path,
                docker_tag=docker_tag, call_args=call_args)

        try:
            self.ctx.log(
                'Running model in deeplearninc/'
                'auger-ml-worker:%s' % docker_tag)
            result_file = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            result_file = result_file.decode("utf-8").strip()
            result_file = os.path.basename(result_file)
            # getattr(subprocess,
            #     'check_call' if self.ctx.debug else 'check_output')(
            #     command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            raise AugerException('Error running Docker container...')

        return os.path.join(data_path, "predictions", result_file)
