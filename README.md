# NYC Airbnb Price Prediction Pipeline 🏙️

# wandb project link 
https://wandb.ai/oyemiadeyemo-teesside-university/nyc_airbnb

This project builds a full machine learning pipeline to predict Airbnb listing prices in New York City. It uses tools like MLflow, Weights & Biases (W&B), Hydra, and scikit-learn.

## 🔧 Project Structure

```
.
├── main.py                  # Pipeline orchestrator
├── src/
│   ├── basic_cleaning/      # Data cleaning step
│   │   └── run.py
│   └── ...                  # Other steps (check_data, train_random_forest, etc.)
├── conda.yml                # Conda environment configuration
├── config/
│   └── config.yaml          # Hydra config file
└── README.md
```

## 🚀 How to Run

Make sure you're in the conda environment and have MLflow installed.

### Run the full pipeline:
```bash
python main.py
```

### Run selected steps:
```bash
python main.py main.steps=download,basic_cleaning
```

## 📦 Key Tools Used

- **MLflow** – Pipeline orchestration and experiment tracking
- **Weights & Biases** – Artifact and metric tracking
- **Hydra** – Configuration management
- **pandas, scikit-learn** – Data processing and modeling

## 📁 Pipeline Steps

1. **download** – Downloads the dataset and logs as a raw artifact
2. **basic_cleaning** – Filters prices and removes outliers
3. **data_check** – Validates schema and checks drift
4. **data_split** – Splits data into train/val/test sets
5. **train_random_forest** – Trains a random forest regressor
6. **test_regression_model** *(optional)* – Tests model on unseen data

## 📝 Notes

- Modify `config.yaml` to adjust hyperparameters, data paths, etc.
- Artifacts and experiments are tracked automatically in W&B and MLflow.
