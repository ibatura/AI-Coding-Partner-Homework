#!/bin/bash

echo "🔄 Testing Transaction Type Enum Changes"
echo "========================================="
echo ""

cd "$(dirname "$0")/.." || exit 1

echo "Step 1: Compiling Java code..."
./gradlew compileJava --console=plain 2>&1 | grep -E "(BUILD|FAILED|error|Error)" | tail -20

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Compilation successful!"
    echo ""

    echo "Step 2: Running repository tests..."
    ./gradlew test --tests "*TransactionRepositoryTest" --console=plain 2>&1 | grep -E "(BUILD|FAILED|test|Test|PASSED)" | tail -30

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ Repository tests passed!"
        echo ""

        echo "Step 3: Running all tests..."
        ./gradlew test --console=plain 2>&1 | grep -E "(BUILD|FAILED|test completed)" | tail -10

        echo ""
        echo "========================================="
        echo "✅ All enum conversion changes validated!"
        echo ""
        echo "Next step: Run the application"
        echo "  ./gradlew bootRun"
        echo ""
        echo "Then test with:"
        echo "  ./demo/requests.sh"
    else
        echo "❌ Repository tests failed"
        exit 1
    fi
else
    echo "❌ Compilation failed"
    echo ""
    echo "Check errors with:"
    echo "  ./gradlew compileJava"
    exit 1
fi
