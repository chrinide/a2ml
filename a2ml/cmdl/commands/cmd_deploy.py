import click
from a2ml.api.a2ml import A2ML
from a2ml.api.utils.context import pass_context


@click.command('deploy', short_help='Deploy trained model.')
@click.argument('model-id', required=True, type=click.STRING)
@click.option('--locally', is_flag=True, default=False,
    help='Download and deploy trained model locally.')
@click.option('--review', is_flag=True, default=True,
    help='Should model support review based on actual data.')
@pass_context
def cmdl(ctx, model_id, locally, review):
    """Deploy trained model."""
    ctx.setup_logger(format='')
    A2ML(ctx).deploy(model_id=model_id, locally=locally, review=review)
