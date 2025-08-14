# FinRisk - Credit Risk Assessment & Fraud Detection Engine

A production-ready, decoupled solution for financial risk assessment and fraud detection using FastAPI and modern Python practices.

## 🏗️ Architecture

The application follows a clean architecture pattern with clear separation of concerns:

```
src/
├── core/           # Shared utilities, config, logging, exceptions
├── domain/         # Business logic, models, services
├── api/           # HTTP layer, routes, controllers
└── infrastructure/ # External services, data access, caching

ml-methodology/     # ML research, models, and methodology (separate)
├── src/           # ML-specific source code
├── notebooks/     # Jupyter notebooks for research
├── data/          # ML data storage
└── scripts/       # ML utility scripts
```

### Key Principles

- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Single Responsibility**: Each class/module has one reason to change
- **Clean Interfaces**: Well-defined contracts between layers
- **ML Separation**: Machine learning components are isolated in `ml-methodology/`

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (recommended)
- PostgreSQL (for production)
- Redis (for caching)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd FinRisk
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## 🔧 API Endpoints

### Credit Risk Assessment

**POST** `/api/credit/assess`

Assess credit risk for a loan application.

```json
{
  "customer_id": "CUST001",
  "loan_amount": 50000,
  "annual_income": 75000,
  "debt_to_income_ratio": 0.35,
  "credit_score": 720,
  "employment_status": "Full-time",
  "years_employed": 5
}
```

**Response:**

```json
{
  "risk_score": 685,
  "decision": "APPROVE",
  "confidence": 0.85,
  "risk_level": "MEDIUM",
  "factors": ["moderate_loan_to_income_ratio"],
  "explanation": {
    "base_credit_score": 720,
    "income_ratio_impact": 0.67,
    "employment_impact": "Full-time",
    "final_score": 685,
    "risk_level": "MEDIUM"
  },
  "processing_time_ms": 45
}
```

### Fraud Detection

**POST** `/api/fraud/detect`

Detect fraud in a transaction.

```json
{
  "customer_id": "CUST001",
  "transaction_id": "TXN123",
  "amount": 2500,
  "merchant_category": "Electronics",
  "location": "New York, USA",
  "device_info": "Mobile Device"
}
```

**Response:**

```json
{
  "fraud_probability": 0.25,
  "decision": "ALLOW",
  "risk_factors": ["moderate_amount", "mobile_device"],
  "processing_time_ms": 32
}
```

## 🏛️ Project Structure

```
FinRisk/
├── src/
│   ├── core/                 # Shared utilities
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── logging.py       # Logging setup
│   │
│   ├── domain/              # Business logic
│   │   ├── __init__.py
│   │   ├── models.py        # Domain models
│   │   ├── credit_risk.py   # Credit risk service
│   │   └── fraud_detection.py # Fraud detection service
│   │
│   ├── api/                 # HTTP layer
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app
│   │   └── routes.py        # API routes
│   │
│   └── infrastructure/      # External services
│       ├── __init__.py
│       ├── data_access.py   # Data repository
│       ├── mlflow_client.py # MLflow integration
│       └── redis_client.py  # Redis caching
│
├── ml-methodology/          # ML research and models
├── tests/                   # Test files
├── deployment/              # Deployment configurations
├── data/                    # Data files
├── logs/                    # Log files
├── deploy.sh               # Deployment script
├── requirements.txt        # Dependencies
├── Dockerfile              # Production Dockerfile
├── docker-compose.prod.yml # Production Docker Compose
└── README.md              # This file
```

## 🔧 Configuration

Configuration is managed through environment variables. See `env.example` for all available options.

Key configuration options:

- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `DEBUG`: Debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL
- `MLFLOW_TRACKING_URI`: MLflow tracking URI

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_credit_risk.py
```

## 📊 Monitoring

The application includes:

- **Health checks**: `/health` endpoint
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured logging with configurable levels
- **MLflow integration**: Model tracking and experiment logging

## 🚀 Deployment Options

### Quick Deployment

1. **Setup environment**
   ```bash
   cp env.production.example .env
   # Edit .env with your production values
   ```

2. **Deploy with script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Docker Deployment

```bash
# Build and run
docker build -t finrisk .
docker run -p 8000:8000 --env-file .env finrisk

# With Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start application
gunicorn src.api.main:app --bind 0.0.0.0:8000 --workers 4
```

## 🔒 Security

- **Authentication**: JWT-based authentication ready
- **Rate Limiting**: Configurable rate limits
- **CORS**: Configurable CORS policies
- **Input Validation**: Pydantic models for validation
- **HTTPS**: Use reverse proxy (nginx) for HTTPS

## 📈 Performance

- **Caching**: Redis for response caching
- **Connection Pooling**: Database connection pooling
- **Async Processing**: FastAPI async support
- **Load Balancing**: Multiple worker processes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information