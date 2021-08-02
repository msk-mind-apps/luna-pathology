import os, json, shutil, click

import luna_core.common.constants as const
from luna_core.common.CodeTimer import CodeTimer
from luna_core.common.config    import ConfigSet

from luna_pathology.common.slideviewer_client import fetch_slide_ids, download_sv_point_annotation

# Dask imports
import dask
import dask.dataframe as dd
from dask.distributed import Client
from luna_core.common.dask import prune_empty_delayed

# Logging imports
import logging
from luna_core.common.custom_logger import init_logger
logger = init_logger(level=logging.INFO)

os.environ['OPENBLAS_NUM_THREADS'] = '1'

# Special function for this CLI
import pandas as pd
def download_point_annotation(slide_id, slideviewer_path, user, project_id, slideviewer_url):
    """Downloads point-click nuclear annotations using slideviewer API

    Args:
        slideviewer_url (string): slideviewer base url e.g. https://slideviewer-url.com
        slideviewer_path (string): slide path in slideviewer
        project_id (string): slideviewer project id
        user (string): username used to create the expert annotation

    Returns:
        json: point-click nuclear annotations
    """
    url = slideviewer_url + "/slides/" + str(user) + "@mskcc.org/projects;" + \
          str(project_id) + ';' + slideviewer_path + "/getSVGLabels/nucleus"

    data = download_sv_point_annotation(url)

    if data == None: return None

    df = pd.DataFrame(data)
    df["slide_id"] = slide_id
    df = df.set_index("slide_id")

    return df

@click.command()
@click.option('-d', '--data_config_file', default=None, type=click.Path(exists=True),
              help="path to yaml file containing data input and output parameters. "
                   "See data_config.yaml.template")
@click.option('-a', '--app_config_file', default='config.yaml', type=click.Path(exists=True),
              help="path to yaml file containing application runtime parameters. "
                   "See config.yaml.template")
def cli(data_config_file, app_config_file):
    """This module generates a parquet table of point-click nuclear annotation jsons.

    The configuration files are copied to your project/configs/table_name folder
    to persist the metadata used to generate the proxy table.

    INPUT PARAMETERS

    app_config_file - path to yaml file containing application runtime parameters. See config.yaml.template

    data_config_file - path to yaml file containing data input and output parameters. See data_config.yaml.template

    - ROOT_PATH: path to output data

    - DATA_TYPE: data type used in table name e.g. POINT_RAW_JSON

    - PROJECT: your project name. used in table path

    - DATASET_NAME: optional, dataset name to version your table

    - PROJECT_ID: Slideviewer project id

    - USERS: list of users that provide expert annotations for this project

    - SLIDEVIEWER_CSV_FILE: an optional path to a SlideViewer csv file to use that lists the names of the whole slide images
    and for which the regional annotation proxy table generator should download point annotations.
    If this field is left blank, then the regional annotation proxy table generator will download this file from SlideViewer.

    TABLE SCHEMA

    - slideviewer_path: path to original slide image in slideviewer platform

    - slide_id: id for the slide. synonymous with image_id

    - sv_project_id: same as the PROJECT_ID from data_config_file, refers to the SlideViewer project number.

    - sv_json: json annotation file downloaded from slideviewer.

    - user: username of the annotator for a given annotation

    - sv_json_record_uuid: hash of raw json annotation file from slideviewer, format: SVPTJSON-{json_hash}
    """
    with CodeTimer(logger, 'generate POINT_RAW_JSON table'):
        logger.info('data config file: ' + data_config_file)
        logger.info('app config file: ' + app_config_file)

        # load configs
        cfg = ConfigSet(name="DATA_CFG", config_file=data_config_file)
        cfg = ConfigSet(name="APP_CFG",  config_file=app_config_file)

        # copy app and data configuration to destination config dir
        config_location = const.CONFIG_LOCATION(cfg)
        os.makedirs(config_location, exist_ok=True)

        if app_config_file==os.path.join(config_location, "app_config.yaml"):
            logger.info ("Using cached app_config, skipping copy (possible user permission issue)!")
        else: 
            shutil.copy(app_config_file, os.path.join(config_location, "app_config.yaml"))
            logger.info(f"{app_config_file} file copied to {config_location}")


        if data_config_file==os.path.join(config_location, "data_config.yaml"):
            logger.info ("Using cached data_config, skipping copy (possible user permission issue)!")
        else: 
            shutil.copy(data_config_file, os.path.join(config_location, "data_config.yaml"))
            logger.info(f"{data_config_file} file copied to {config_location}")


        create_proxy_table()


def create_proxy_table():
    """Create a proxy table of point annotation json files downloaded from the SlideViewer API

    Each row of the table is a point annotation json created by a user for a slide.

    Returns:
        None
    """

    cfg = ConfigSet()

    client = Client(n_workers=4, threads_per_worker=4)
    client.run(init_logger)
    logger.info (f"Initialized dask client: {client}")

    # load paths from configs
    POINT_TABLE_PATH = const.TABLE_LOCATION(cfg)

    PROJECT_ID      = cfg.get_value(path='DATA_CFG::PROJECT_ID')
    SLIDEVIEWER_URL = cfg.get_value(path='DATA_CFG::SLIDEVIEWER_URL')

    # Get slide list to use
    # Download CSV file in the project configs dir
    df_slides = fetch_slide_ids(
        SLIDEVIEWER_URL, 
        PROJECT_ID, const.CONFIG_LOCATION(cfg),
        cfg.get_value(path='DATA_CFG::SLIDEVIEWER_CSV_FILE'), 
        as_df=True)

    l_users  = cfg.get_value('DATA_CFG::USERS')

    logger.info("Got slide listing!!")
    logger.info(df_slides)
    logger.info(l_users)

    # Prepare
    d_download_point_annotation = dask.delayed(download_point_annotation)

    outputs = []
    logger.info(f"Submitting {len(df_slides) * len(l_users)} tasks!!")
    for _, row in df_slides.iterrows():
        for user in l_users:
            outputs.append( d_download_point_annotation(row.slide_id, row.slideviewer_path, user, PROJECT_ID, SLIDEVIEWER_URL) )
    
    # We have to prune our tasks for only filled dataframes
    ddf = dd.from_delayed(prune_empty_delayed(outputs))
    logger.info (f"Proxy table:\n{ddf.head()}")

    logger.info(f"Saving table -> {POINT_TABLE_PATH}")

    # Now we can use dasks's paralellism in the backend to write our tables!
    ddf.to_parquet(POINT_TABLE_PATH)

    logger.info("Done.")

if __name__ == "__main__":
    cli()
