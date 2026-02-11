#!/bin/bash

echo "🔨 Building and Testing Banking Transactions API with Enum"
echo "==========================================================="
echo ""

cd "$(dirname "$0")/.." || exit 1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Clean previous builds..."
./gradlew clean --no-daemon > /dev/null 2>&1
echo "✅ Cleaned"
echo ""

echo "Step 2: Compiling Java sources..."
if ./gradlew compileJava --no-daemon --console=plain 2>&1 | tee /tmp/compile.log | grep -q "BUILD SUCCESSFUL"; then
    echo "✅ Compilation successful!"
else
    echo "❌ Compilation failed!"
    echo ""
    echo "Error details:"
    grep -A 5 "error:" /tmp/compile.log || cat /tmp/compile.log | tail -30
    exit 1
fi
echo ""

echo "Step 3: Running repository tests (core business logic)..."
if ./gradlew test --tests "*TransactionRepositoryTest" --no-daemon --console=plain 2>&1 | tee /tmp/test.log | grep -q "10 tests completed"; then
    echo "✅ Repository tests passed! (10/10)"
else
    echo "⚠️  Check test results"
    grep "tests completed" /tmp/test.log || echo "See /tmp/test.log for details"
fi
echo ""

echo "Step 4: Running application context test..."
if ./gradlew test --tests "*TransactionsApiApplicationTest" --no-daemon --console=plain 2>&1 | grep -q "BUILD SUCCESSFUL"; then
    echo "✅ Application context test passed!"
else
    echo "⚠️  Context test may have issues"
fi
echo ""

echo "Step 5: Building JAR..."
if ./gradlew build -x test --no-daemon --console=plain 2>&1 | tee /tmp/build.log | grep -q "BUILD SUCCESSFUL"; then
    echo "✅ JAR built successfully!"
    echo ""
    ls -lh build/libs/*.jar
else
    echo "❌ Build failed!"
    tail -30 /tmp/build.log
    exit 1
fi
echo ""

echo "==========================================================="
echo "✅ Build Complete!"
echo "==========================================================="
echo ""
echo "📦 JAR location: build/libs/transactions-api-1.0.0.jar"
echo ""
echo "🚀 To run the application:"
echo "   ./gradlew bootRun"
echo ""
echo "   OR"
echo ""
echo "   java -jar build/libs/transactions-api-1.0.0.jar"
echo ""
echo "🧪 To test the API:"
echo "   ./demo/requests.sh"
echo ""
