# Multi-Agent System for Munder Difflin Paper Company

[![CI](https://github.com/yourusername/multi-agent-system/workflows/CI/badge.svg)](https://github.com/yourusername/multi-agent-system/actions)
[![codecov](https://codecov.io/gh/yourusername/multi-agent-system/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/multi-agent-system)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A **production-ready, industry-grade multi-agent system** for automating business operations at Munder Difflin Paper Company. This project demonstrates advanced software engineering practices combined with modern agentic AI patterns.

## 🎯 Overview

This system coordinates four specialized AI agents to handle:
- **Inventory Management**: Stock monitoring, reorder decisions, supplier coordination
- **Quote Generation**: Pricing calculations, bulk discounts, historical analysis
- **Order Fulfillment**: Order processing, inventory allocation, transaction recording
- **Orchestration**: Workflow coordination, intent routing, customer communication

## ✨ Features

### Core Capabilities
- 🤖 **Multi-Agent Architecture**: Specialized agents with clear responsibilities
- 🔄 **Workflow Orchestration**: Seamless coordination between agents
- 💾 **Database Management**: SQLAlchemy ORM with Alembic migrations
- 🌐 **REST API**: FastAPI with automatic OpenAPI documentation
- 📊 **Financial Reporting**: Real-time cash balance and inventory valuation
- 🔍 **Historical Analysis**: Quote history search and pricing guidance

### Advanced Features
- ⚡ **Caching Layer**: Redis for performance optimization
- 🔄 **Background Jobs**: Celery for async processing
- 📈 **Observability**: Structured logging, metrics, and tracing
- 🧪 **Comprehensive Testing**: Unit, integration, and e2e tests
- 🐳 **Containerization**: Docker and Docker Compose setup
- 🔐 **Security**: Rate limiting, API authentication, secrets management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                         │
│                     (FastAPI REST API)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Orchestration Layer                     │
│         (Orchestrator + Specialized Agents)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                        │
│        (Services, Repositories, Domain Models)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Data Access Layer                          │
│              (SQLAlchemy ORM + Alembic)                         │
└─────────────────────────────────────────────────────────────────┘
```

For detailed architecture documentation, see [docs/architecture/system-design.md](docs/architecture/system-design.md).

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Redis (optional, for caching)
- PostgreSQL (optional, SQLite works for development)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-agent-system.git
cd multi-agent-system

# Install dependencies
make setup

# Configure environment
cp .env.example .env
# Edit .env with your settings (especially OPENAI_API_KEY)

# Initialize database
make init-db

# Seed with sample data
make seed
```

### Running the Application

```bash
# Start the API server
make run

# In another terminal, start the worker (optional)
make run-worker

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Using Docker

```bash
# Build and start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## 📚 Documentation

- [📖 Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed roadmap and learning guide
- [🏛️ Architecture](docs/architecture/system-design.md) - System design and patterns
- [🤖 Agent Design](docs/architecture/agent-design.md) - Agent communication patterns
- [💾 Database Schema](docs/architecture/database-schema.md) - Data model documentation
- [🌐 API Design](docs/architecture/api-design.md) - API specifications
- [🚢 Deployment Guide](docs/deployment/production-deployment.md) - Production deployment
- [🧪 Testing Guide](docs/guides/testing-guide.md) - Testing strategies
- [👩‍💻 Development Guide](docs/guides/development-guide.md) - Development best practices

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Run type checks
make typecheck

# Run linting
make lint
```

## 📊 Project Structure

```
multi-agent-system/
├── src/multi_agent_system/     # Main application code
│   ├── api/                    # FastAPI application
│   ├── agents/                 # Agent implementations
│   ├── core/                   # Core utilities
│   ├── database/               # Database layer
│   ├── domain/                 # Domain models
│   ├── services/               # Business logic
│   └── utils/                  # Utility functions
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
├── docs/                       # Documentation
├── docker/                     # Docker configuration
├── scripts/                    # Utility scripts
└── pyproject.toml             # Project configuration
```

## 🎓 Learning Outcomes

This project demonstrates:

### Software Engineering
- **Architecture Patterns**: Layered architecture, repository pattern, dependency injection
- **API Design**: RESTful principles, request/response modeling, error handling
- **Database Design**: ORM patterns, migrations, query optimization
- **Testing Strategies**: Unit, integration, and e2e testing with high coverage
- **DevOps Practices**: Containerization, CI/CD pipelines, monitoring

### Agentic AI
- **Agent Design Patterns**: Orchestrator pattern, specialized agents, tool use
- **Prompt Engineering**: System prompts, few-shot learning, chain-of-thought
- **Agent Communication**: Message passing, state management, workflow orchestration
- **LLM Integration**: API integration, error handling, cost optimization

## 🛠️ Development

### Common Commands

```bash
make help              # Show all available commands
make dev               # Install dev dependencies
make run               # Start API server
make test              # Run tests
make format            # Format code
make lint              # Run linter
make typecheck         # Run type checks
make docker-up         # Start all services
```

### Adding a New Agent

1. Create agent class in `src/multi_agent_system/agents/`
2. Define agent tools in `src/multi_agent_system/agents/tools/`
3. Add prompts in `src/multi_agent_system/agents/prompts/`
4. Register agent in orchestrator
5. Add tests in `tests/unit/test_agents/`

See [Development Guide](docs/guides/development-guide.md) for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/guides/contributing.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original concept from Udacity AI Agents course
- Built with [pydantic-ai](https://github.com/pydantic/pydantic-ai)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)

## 📧 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/multi-agent-system](https://github.com/yourusername/multi-agent-system)

---

**⭐ If you find this project helpful, please consider giving it a star!**

