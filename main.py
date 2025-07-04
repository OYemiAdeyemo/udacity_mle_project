import json

import mlflow
import tempfile
import os
import wandb
import hydra
from omegaconf import DictConfig
import pandas as pd

_steps = [
    "download",
    "basic_cleaning",
    "data_check",
    "data_split",
    "train_random_forest",
    # NOTE: We do not include this in the steps so it is not run by mistake.
    # You first need to promote a model export to "prod" before you can run this,
    # then you need to run this step explicitly
#    "test_regression_model"
]


# This automatically reads in the configuration
@hydra.main(config_name='config')
def go(config: DictConfig):

    # Setup the wandb experiment. All runs will be grouped under this name
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    # Steps to execute
    steps_par = config['main']['steps']
    active_steps = steps_par.split(",") if steps_par != "all" else _steps

    # Move to a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:

        if "download" in active_steps:
            # Download file and load in W&B
            _ = mlflow.run(
                f"{config['main']['components_repository']}/get_data",
                "main",
                version='main',
                env_manager="conda",
                parameters={
                    "sample": config["etl"]["sample"],
                    "artifact_name": "sample.csv",
                    "artifact_type": "raw_data",
                    "artifact_description": "Raw file as downloaded"
                },
            )

        if "basic_cleaning" in active_steps:
            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "basic_cleaning"),
                "main",
                parameters={
                "input_artifact": "sample.csv:latest",
                "output_artifact": "clean_sample.csv",
                "output_type": "clean_sample",
                "output_description": "Data with outliers and null values removed",
                "min_price": config['etl']['min_price'],
                "max_price": config['etl']['max_price']
                },
    )
            pass


        # Load the data
        df = pd.read_csv(args.input_artifact)

        # Filter by price
        idx_price = df['price'].between(args.min_price, args.max_price)
        df = df[idx_price].copy()

        # Filter by location
        idx_geo = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
        df = df[idx_geo].copy()

        if "data_check" in active_steps:
            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "check_data"),
                "main",
                parameters={
                "csv": "clean_sample.csv:v0",
                "ref": "clean_sample.csv:reference",
                "kl_threshold": config["data_check"]["kl_threshold"],
                "ks_alpha": config["data_check"]["ks_alpha"],
                "min_price":10,
                "max_price":350
                },
    )

            pass

        if "data_split" in active_steps:
            _ = mlflow.run(
                f"{config['main']['components_repository']}/train_val_test_split",
                "main",
                parameters={
                # The input is the cleaned data from the previous step
                "input_artifact": "clean_sample.csv:v0",
                
                # Fraction of the data to allocate for the test set
                "test_size": config["modeling"]["test_size"],
                
                # Fraction of the *remaining* data to allocate for the validation set
                "val_size": config["modeling"]["val_size"],

                # Seed for reproducibility
                "random_seed": config["modeling"]["random_seed"],
                
                # Column to use for stratification, ensuring similar distributions in splits
                "stratify_by": config["modeling"]["stratify_by"]
                },
            )
            pass

        if "train_random_forest" in active_steps:

            # NOTE: we need to serialize the random forest configuration into JSON
            rf_config = os.path.abspath("rf_config.json")
            with open(rf_config, "w+") as fp:
                json.dump(dict(config["modeling"]["random_forest"].items()), fp)  # DO NOT TOUCH

            # NOTE: use the rf_config we just created as the rf_config parameter for the train_random_forest
            # step

            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src","train_random_forest"),
                entry_point="main",
                parameters={
                "trainval_artifact": "trainval_data.csv:latest",
                "rf_config": rf_config,
                "output_artifact": config["modeling"]["train_random_forest"]["export_artifact"],
                "random_seed": config["modeling"]["random_seed"],
                "val_size": config["modeling"]["test_size"],
                "stratify_by": config["modeling"]["stratify_by"],
                "max_tfidf_features": config["modeling"]["max_tfidf_features"],
                },
            )

            pass

        if "test_regression_model" in active_steps:

            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "test_regression_model"),
                entry_point="main",
                parameters={
                    "mlflow_model": "random_forest_export:prod",
                    "test_artifact": "test_data.csv:latest"
                },
            )

            pass


if __name__ == "__main__":
    go()
