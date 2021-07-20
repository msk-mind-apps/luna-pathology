
# General imports
import os, json, logging
import click

# From common
from luna_core.common.custom_logger   import init_logger
from luna_core.common.DataStore       import DataStore_v2
from luna_core.common.config          import ConfigSet

# From radiology.common
from luna_pathology.common.preprocess   import pretile_scoring

@click.command()
@click.option('-a', '--app_config', required=True,
              help="application configuration yaml file. See config.yaml.template for details.")
@click.option('-s', '--datastore_id', required=True,
              help='datastore name. usually a slide id.')
@click.option('-m', '--method_param_path', required=True,
              help='json file with method parameters for tile generation and filtering.')
def cli(app_config, datastore_id, method_param_path):
    """Generate tile addresses, scores and optionally annotation labels."""
    init_logger()

    with open(method_param_path) as json_file:
        method_data = json.load(json_file)
    generate_tile_labels_with_datastore(app_config, datastore_id, method_data)

def generate_tile_labels_with_datastore(app_config: str, datastore_id: str, method_data: dict):
    """Generate tile addresses, scores and optionally annotation labels.

    Args:
        app_config (string): path to application configuration file.
        datastore_id (string): datastore name. usually a slide id.
        method_data (dict): method parameters including input, output details.

    Returns:
        None
    """
    logger = logging.getLogger(f"[datastore={datastore_id}]")

    # Do some setup
    cfg = ConfigSet("APP_CFG", config_file=app_config)
    datastore   = DataStore_v2(method_data.get("root_path"))
    method_id   = method_data.get("job_tag", "none")

    image_path  = datastore.get(datastore_id, method_data['input_wsi_tag'], "WholeSlideImage")
    logger.info(f"Whole slide image path: {image_path}")

    # get image_id
    # TODO - allow -s to take in slide (datastore_id) id
    image_id = datastore_id

    try:
        if image_path is None:
            raise ValueError("Image node not found")

        # Data just goes under namespace/name
        # TODO: This path is really not great, but works for now
        output_dir = os.path.join(method_data.get("root_path"), datastore_id, method_id, "TileImages", "data")
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        logger.info(f"Writing to output dir: {output_dir}")
        properties = pretile_scoring(image_path, output_dir, method_data.get("annotation_table_path"), method_data, image_id)

    except Exception as e:
        logger.exception (f"{e}, stopping job execution...")
        raise e

    with open(os.path.join(output_dir, "metadata.json"), "w") as fp:
        json.dump(properties, fp)

if __name__ == "__main__":
    cli()
