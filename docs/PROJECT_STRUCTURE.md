# QuerySense Project Structure

This document outlines the complete project structure for QuerySense - Internal Knowledge Assistant.

## Directory Overview

```
QuerySense/
├── README.md                    # Main project documentation
├── package.json                 # Root package.json for workspace management
├── Cargo.toml                   # Rust workspace configuration
├── docker-compose.yml           # Development environment services
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
│
├── frontend/                    # Next.js 14 Frontend Application
│   ├── src/
│   │   ├── app/                 # App Router (Next.js 14)
│   │   ├── components/          # Reusable UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities and configurations
│   │   ├── store/               # Zustand state management
│   │   └── types/               # TypeScript type definitions
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                     # Backend Services
│   ├── api-server/              # Main Rust API Server (Axum)
│   │   ├── src/
│   │   │   ├── handlers/        # HTTP request handlers
│   │   │   ├── models/          # Data models
│   │   │   ├── services/        # Business logic
│   │   │   ├── middleware/      # Custom middleware
│   │   │   ├── utils/           # Utility functions
│   │   │   └── main.rs          # Application entry point
│   │   ├── Cargo.toml
│   │   └── .env.example
│   │
│   ├── ai-service/              # Python AI/ML Service (FastAPI)
│   │   ├── app/
│   │   │   ├── models/          # AI models and embeddings
│   │   │   ├── services/        # AI processing services
│   │   │   ├── routers/         # API routes
│   │   │   └── main.py          # FastAPI application
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .env.example
│   │
│   └── realtime-service/        # Node.js Real-time Service (Socket.IO)
│       ├── src/
│       │   ├── handlers/        # Socket event handlers
│       │   ├── middleware/      # Socket middleware
│       │   └── server.ts        # Socket.IO server
│       ├── package.json
│       └── tsconfig.json
│
├── browser-extension/           # Browser Extension
│   ├── src/
│   │   ├── popup/               # Extension popup UI
│   │   ├── content/             # Content scripts
│   │   ├── background/          # Background service worker
│   │   └── shared/              # Shared utilities
│   ├── manifest.json
│   ├── package.json
│   └── webpack.config.js
│
├── infrastructure/              # DevOps and Infrastructure
│   ├── docker/                  # Docker configurations
│   │   ├── postgres/
│   │   │   └── init.sql         # Database initialization
│   │   ├── api-server/
│   │   │   └── Dockerfile
│   │   ├── ai-service/
│   │   │   └── Dockerfile
│   │   └── frontend/
│   │       └── Dockerfile
│   │
│   └── k8s/                     # Kubernetes manifests
│       ├── namespace.yaml
│       ├── configmap.yaml
│       ├── secrets.yaml
│       ├── postgres.yaml
│       ├── redis.yaml
│       ├── api-server.yaml
│       ├── ai-service.yaml
│       ├── frontend.yaml
│       └── ingress.yaml
│
├── docs/                        # Documentation
│   ├── api/                     # API documentation
│   ├── deployment/              # Deployment guides
│   ├── development/             # Development setup
│   └── architecture/            # System architecture docs
│
├── scripts/                     # Utility scripts
│   ├── setup.sh                 # Development environment setup
│   ├── build.sh                 # Build script
│   ├── deploy.sh                # Deployment script
│   └── migrate.sh               # Database migration script
│
└── tests/                       # Integration and E2E tests
    ├── e2e/                     # End-to-end tests
    ├── integration/             # Integration tests
    └── load/                    # Load testing scripts
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.4
- **State Management**: Zustand + React Query
- **Forms**: React Hook Form + Zod
- **Testing**: Vitest + Testing Library + Playwright

### Backend
- **API Server**: Rust with Axum framework
- **AI Service**: Python with FastAPI
- **Real-time**: Node.js with Socket.IO
- **Database**: PostgreSQL 16 with pgvector
- **Cache**: Redis 7
- **Search**: ElasticSearch 8
- **Storage**: MinIO (S3-compatible)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## Getting Started

1. **Clone the repository**
2. **Copy environment variables**: `cp .env.example .env`
3. **Start services**: `npm run docker:up`
4. **Install dependencies**: `npm run install:all`
5. **Start development**: `npm run dev`

## Development Workflow

1. **Frontend Development**: `npm run dev:frontend`
2. **Backend Development**: `npm run dev:backend`
3. **AI Service Development**: `npm run dev:ai`
4. **Real-time Service**: `npm run dev:realtime`

## Next Steps

1. Initialize frontend with Next.js 14
2. Set up Rust API server structure
3. Create Python AI service foundation
4. Implement basic authentication
5. Build core Q&A functionality
