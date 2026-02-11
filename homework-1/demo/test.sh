#!/bin/bash

echo "🧪 Running All Tests for Banking Transactions API"
echo "=================================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Run all tests with detailed output
echo "Running unit tests and integration tests..."
echo ""

./gradlew test --info

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ All tests passed successfully!"
    echo "=================================================="
    echo ""
    echo "📊 Test Report available at:"
    echo "   build/reports/tests/test/index.html"
    echo ""
    echo "Open in browser:"
    echo "   open build/reports/tests/test/index.html"
    echo ""
else
    echo ""
    echo "=================================================="
    echo "❌ Some tests failed. Check the output above."
    echo "=================================================="
    echo ""
    echo "📊 Detailed test report:"
    echo "   build/reports/tests/test/index.html"
    echo ""
    exit 1
fi
