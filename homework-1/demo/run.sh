#!/bin/bash

echo "🚀 Starting Banking Transactions API..."
echo ""

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java is not installed. Please install Java 17 or higher first."
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Build and run the application
echo "📦 Building the application..."
./gradlew clean build -x test

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo "🏃 Running the application..."
    echo ""
    ./gradlew bootRun
else
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi
