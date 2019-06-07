import click

from a2ml.cmdl.utils.test_task import TestTask
from a2ml.cmdl.utils.context import pass_context
from a2ml.api.auger.train import AugerTrain
from a2ml.cmdl.utils.provider_operations import ProviderOperations
from a2ml.api import gc_a2ml
from a2ml.api.google.train import GoogleTrain
class TrainCmd(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def train(self):
        operations = {
            'auger': AugerTrain(self.ctx.copy('auger')).train,
            'google': GoogleTrain(self.ctx.copy('google')).train,
            'azure': TestTask(self.ctx.copy('azure')).iterate
        }
        ProviderOperations(self.ctx).execute(self.ctx.get_providers(), operations)

@click.command('train', short_help='Train the model.')
@pass_context
def cmdl(ctx):
    """Train the model."""
    ctx.setup_logger(format='')
    TrainCmd(ctx).train()