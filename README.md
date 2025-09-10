# GenAI Metrics Dashboard

> **Enterprise Project Management Platform with Comprehensive Logging & AI Integration**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/ashishrb/project-management-framework)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)](https://postgresql.org)
[![Ollama](https://img.shields.io/badge/Ollama-AI%20Models-purple)](https://ollama.ai)

## 🚀 Overview

The GenAI Metrics Dashboard is a comprehensive enterprise project management platform that combines traditional project management capabilities with advanced AI features powered by Ollama models. Built with FastAPI, PostgreSQL, and modern web technologies, it provides real-time insights, predictive analytics, and intelligent project management assistance.

## ✨ Key Features

### 📊 **Core Project Management**
- **Project Tracking**: Complete project lifecycle management
- **Resource Management**: Team and resource allocation tracking
- **Risk Management**: Risk identification and mitigation strategies
- **Real-time Dashboard**: Live project status and metrics
- **WebSocket Integration**: Real-time updates and notifications

### 🤖 **AI-Powered Features**
- **AI Copilot**: Intelligent project management assistance
- **Predictive Analytics**: Project completion probability and risk forecasting
- **Smart Insights**: AI-generated recommendations and insights
- **RAG Knowledge System**: Intelligent document search and retrieval
- **Automated Reporting**: AI-generated project reports and summaries

### 🔧 **Advanced Capabilities**
- **Comprehensive Logging**: Detailed logging system for debugging and monitoring
- **Performance Optimization**: Database optimization and caching strategies
- **Real-time Monitoring**: Live system performance and health monitoring
- **Scalable Architecture**: Designed for enterprise-scale deployments

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Advanced ORM with database migrations
- **PostgreSQL**: Robust relational database
- **Redis**: Caching and session management
- **WebSockets**: Real-time communication
- **Ollama**: AI model integration and management

### Frontend Stack
- **Vanilla JavaScript**: Modern ES6+ with modular architecture
- **Chart.js**: Interactive data visualization
- **Bootstrap**: Responsive UI framework
- **WebSocket Client**: Real-time updates
- **Progressive Web App**: Offline capabilities

### AI Integration
- **Ollama Models**: Multiple specialized AI models
- **RAG System**: Retrieval-Augmented Generation for knowledge queries
- **Vector Database**: ChromaDB for semantic search
- **Context Management**: Intelligent conversation context handling

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Ollama (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ashishrb/project-management-framework.git
cd project-management-framework
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database**
```bash
# Run database migrations
alembic upgrade head

# Seed initial data
python scripts/seed_lookup_data.py
python scripts/generate_demo_data.py
```

5. **Start the application**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access the dashboard**
- Open http://localhost:8000/dashboard
- API documentation: http://localhost:8000/docs

## 📁 Project Structure

```
project-management-framework/
├── app/                          # Backend application
│   ├── api/                      # API endpoints
│   ├── core/                     # Core functionality
│   │   └── logging.py            # Comprehensive logging system
│   ├── models/                   # Database models
│   ├── schemas/                  # Pydantic schemas
│   ├── routes/                   # View routes
│   └── websocket/                # WebSocket handlers
├── static/                       # Frontend assets
│   ├── js/                       # JavaScript modules
│   │   ├── dashboard.js          # Dashboard functionality
│   │   ├── logging.js            # Frontend logging
│   │   ├── navigation.js         # Navigation system
│   │   └── main.js               # Core utilities
│   └── css/                      # Stylesheets
├── templates/                    # HTML templates
├── scripts/                      # Utility scripts
│   ├── analyze_logs.py           # Log analysis tool
│   ├── monitor_logs.py           # Real-time log monitoring
│   └── generate_demo_data.py     # Demo data generation
├── docs/                         # Documentation
│   ├── analysis/                 # Technical analysis
│   └── archive/                  # Archived documentation
├── logs/                         # Application logs
├── tests/                        # Test suite
└── alembic/                      # Database migrations
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379

# AI Models
OLLAMA_BASE_URL=http://localhost:11434
AI_MODELS_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

### AI Model Configuration
```python
AI_MODELS = {
    "primary": "llama3:8b",                    # Main conversational AI
    "fast": "llama3.2:3b-instruct-q4_K_M",     # Quick responses
    "analysis": "mistral:7b-instruct-v0.2-q4_K_M",  # Structured analysis
    "code": "codellama:7b-instruct-q4_K_M",    # Code-related tasks
    "embedding": "nomic-embed-text:latest"      # Document embeddings
}
```

## 📊 Monitoring & Debugging

### Comprehensive Logging System
The platform includes a sophisticated logging system for easy debugging and monitoring:

```bash
# Monitor logs in real-time
python scripts/monitor_logs.py

# Analyze all logs
python scripts/analyze_logs.py --verbose

# Check specific errors
tail -f logs/errors.log
```

### Performance Monitoring
- **Database Performance**: Query optimization and index monitoring
- **API Performance**: Response time tracking and optimization
- **AI Performance**: Model response time and accuracy monitoring
- **Memory Usage**: Memory leak detection and optimization

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/ai/
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **AI Tests**: AI model integration testing
- **Performance Tests**: Load and stress testing

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale web=3
```

### Production Considerations
- **Database Optimization**: Proper indexing and query optimization
- **Caching Strategy**: Redis caching for performance
- **Load Balancing**: Multiple application instances
- **Monitoring**: Comprehensive logging and metrics
- **Security**: HTTPS, authentication, and authorization

## 📈 Performance Optimization

### Database Optimization
- **Indexes**: Optimized database indexes for fast queries
- **Query Optimization**: N+1 query prevention and optimization
- **Connection Pooling**: Efficient database connection management
- **Caching**: Redis caching for frequently accessed data

### AI Performance
- **Model Selection**: Intelligent model selection based on task requirements
- **Response Caching**: Cache AI responses for improved performance
- **Load Balancing**: Distribute AI requests across available models
- **Performance Monitoring**: Track AI model performance and accuracy

## 🤖 AI Features

### AI Copilot
- **Project Analysis**: Intelligent project status analysis
- **Risk Assessment**: AI-powered risk identification and mitigation
- **Resource Optimization**: Smart resource allocation suggestions
- **Timeline Optimization**: AI-driven project timeline recommendations

### Predictive Analytics
- **Completion Probability**: Predict project completion likelihood
- **Resource Forecasting**: Forecast future resource requirements
- **Risk Trends**: Analyze risk patterns across projects
- **Budget Predictions**: Predict budget variance and requirements

### RAG Knowledge System
- **Document Search**: Semantic search across project documents
- **Knowledge Retrieval**: Intelligent knowledge base queries
- **Best Practices**: AI-recommended best practices
- **Lessons Learned**: Extract insights from project history

## 📚 Documentation

### Comprehensive Guides
- **[Implementation Strategy](IMPLEMENTATION_STRATEGY.md)**: Complete implementation roadmap
- **[Performance Analysis](docs/analysis/PERFORMANCE_ANALYSIS.md)**: Performance optimization guide
- **[AI Integration Strategy](docs/analysis/AI_INTEGRATION_STRATEGY.md)**: AI implementation guide
- **[Logging System](LOGGING_SYSTEM.md)**: Comprehensive logging documentation
- **[Debugging Guide](DEBUGGING_GUIDE.md)**: Step-by-step debugging process

### API Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features and modular architecture
- **Testing**: Maintain 95%+ test coverage
- **Documentation**: Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern web framework for Python
- **Ollama**: AI model integration platform
- **PostgreSQL**: Robust database system
- **Chart.js**: Interactive data visualization
- **Bootstrap**: Responsive UI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ashishrb/project-management-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ashishrb/project-management-framework/discussions)
- **Documentation**: [Project Wiki](https://github.com/ashishrb/project-management-framework/wiki)

---

**Built with ❤️ for modern project management**
