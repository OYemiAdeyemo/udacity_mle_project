#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""

import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")
    run.config.update(args)

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    logger.info(f"Reading data from {artifact_path}")
    df = pd.read_csv(artifact_path)

    # Price filter
    min_price = float(args.min_price)
    max_price = float(args.max_price)
    logger.info(f"Filtering data with price between {min_price} and {max_price}")
    df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]

    # Geo filter
    logger.info("Filtering data within valid longitude/latitude bounds")
    idx_geo = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx_geo].copy()

    # Save cleaned data
    cleaned_file = "clean_sample.csv"
    df.to_csv(cleaned_file, index=False)
    logger.info(f"Saved cleaned data to {cleaned_file}")

    # Log cleaned data as W&B artifact
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(cleaned_file)
    run.log_artifact(artifact)

    run.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument("--input_artifact", type=str, required=True, help="Input W&B artifact (e.g. sample.csv:latest)")
    parser.add_argument("--output_artifact", type=str, required=True, help="Name for the output artifact")
    parser.add_argument("--output_type", type=str, required=True, help="Type of the output artifact")
    parser.add_argument("--output_description", type=str, required=True, help="Description of the output artifact")
    parser.add_argument("--min_price", type=float, required=True, help="Minimum acceptable price (e.g. 10)")
    parser.add_argument("--max_price", type=float, required=True, help="Maximum acceptable price (e.g. 350)")

    args = parser.parse_args()
    go(args)
