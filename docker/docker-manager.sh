#!/bin/bash

# Nexus Docker Management Script
# Usage: ./docker-manager.sh [dev|prod|stop|logs|clean]

set -e

DOCKER_DIR="servers/docker"
ENV_FILE=""

case "${1:-dev}" in
    "dev")
        echo "🚀 Starting Nexus Development Environment..."
        ENV_FILE="./env.dev.example"
        if [ ! -f "../.env.dev" ]; then
            echo "⚠️  .env.dev not found, copying from example..."
            cp "./env.dev.example" "../.env.dev"
            echo "📝 Please edit servers/.env.dev with your actual secrets and passwords"
        fi
        ENV_FILE="../.env.dev"
        docker-compose -p nexus-servers -f docker-compose.yml -f docker-compose.dev.yml --env-file "$ENV_FILE" up --build
        ;;
    "prod")
        echo "🏭 Starting Nexus Production Environment..."
        ENV_FILE="./env.prod.example"
        if [ ! -f "../.env.prod" ]; then
            echo "⚠️  .env.prod not found, copying from example..."
            cp "./env.prod.example" "../.env.prod"
            echo "📝 Please edit servers/.env.prod with your actual secrets, passwords, and SSD path"
        fi
        ENV_FILE="../.env.prod"
        docker-compose -p nexus-servers -f docker-compose.yml -f docker-compose.prod.yml --env-file "$ENV_FILE" up -d --build

        ;;
    "stop")
        echo "🛑 Stopping Nexus Services..."
        docker-compose down
        ;;
    "logs")
        echo "📋 Showing Nexus Service Logs..."
        docker-compose logs -f "${2:-}"
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        ;;
    "ps")
        echo "📊 Nexus Service Status:"
        docker-compose ps
        ;;
    "db")
        echo "🗄️  Connecting to PostgreSQL..."
        docker-compose exec postgres psql -U postgres -d nexus_db
        ;;
    *)
        echo "Usage: $0 [dev|prod|stop|logs|clean|ps|db]"
        echo ""
        echo "Commands:"
        echo "  dev    - Start development environment with hot reload"
        echo "  prod   - Start production environment"
        echo "  stop   - Stop all services"
        echo "  logs   - Show logs (optionally specify service name)"
        echo "  clean  - Stop services and clean up volumes/images"
        echo "  ps     - Show service status"
        echo "  db     - Connect to PostgreSQL database"
        echo ""
        echo "Examples:"
        echo "  $0 dev                    # Start development"
        echo "  $0 prod                   # Start production"
        echo "  $0 logs graphql          # Show GraphQL logs"
        echo "  $0 db                    # Connect to database"
        exit 1
        ;;
esac
