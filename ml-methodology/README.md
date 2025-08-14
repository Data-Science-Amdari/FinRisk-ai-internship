# FinRisk ML Methodology

This directory contains the machine learning methodology, models, and research components for the FinRisk project. It is separate from the main application to maintain clean separation between the ML research/development and the production API.

## 📁 Structure

```
ml-methodology/
├── src/                    # ML source code
│   ├── data_generation/    # Synthetic data generation
│   ├── feature_engineering/ # Feature engineering pipeline
│   ├── credit_models/      # Credit scoring models
│   ├── fraud_detection/    # Fraud detection algorithms
│   ├── api/               # ML-specific API endpoints
│   └── monitoring/        # Model monitoring and tracking
├── data/                  # Data storage
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed data
│   └── synthetic/        # Synthetic data
├── notebooks/            # Jupyter notebooks
│   ├── exploratory/      # Data exploration
│   ├── modeling/         # Model development
│   └── validation/       # Model validation
├── tests/               # ML-specific tests
├── config/              # ML configuration files
├── docs/               # ML documentation
└── scripts/            # ML utility scripts
```

## 🚀 Usage

### For ML Development

1. **Navigate to the ML methodology directory:**

   ```bash
   cd ml-methodology
   ```

2. **Install ML-specific dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run ML experiments:**

   ```bash
   python scripts/train_models.py
   ```

4. **Start ML API (for model serving):**
   ```bash
   python scripts/run_api.py
   ```

### For Production Integration

The main application (`src/`) imports and uses the trained models from this methodology directory. Models are versioned and tracked using MLflow.

## 🔧 Key Components

- **Credit Models**: XGBoost, LightGBM, and ensemble models for credit scoring
- **Fraud Detection**: Isolation Forest, velocity rules, and anomaly detection
- **Feature Engineering**: Automated feature extraction and preprocessing
- **Model Monitoring**: Performance tracking and drift detection
- **Data Generation**: Synthetic data for testing and validation

## 📊 Model Management

Models are versioned and tracked using MLflow. The main application loads the latest production models from the MLflow registry.

## 🔄 Integration with Main App

The main application (`src/`) imports models and utilities from this directory:

```python
# Example: Loading a credit model
from ml_methodology.src.credit_models.xgboost_model import XGBoostCreditModel
```

## 📝 Development Workflow

1. **Research & Development**: Use notebooks for exploration
2. **Model Training**: Use scripts for reproducible training
3. **Validation**: Test models thoroughly before deployment
4. **Integration**: Export models to main application
5. **Monitoring**: Track model performance in production
