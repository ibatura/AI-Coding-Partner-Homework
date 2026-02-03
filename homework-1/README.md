# 🏦 Banking Transactions REST API

A simple and clean REST API for managing banking transactions, built with **Java Spring Boot** and in-memory storage.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Development Commands](#-development-commands)

---

## ✨ Features

- ✅ Create banking transactions (deposit, withdrawal, transfer)
- ✅ List all transactions
- ✅ Get transaction by ID
- ✅ Check account balance
- ✅ Input validation with meaningful error messages
- ✅ In-memory storage (no database required)
- ✅ RESTful API design with proper HTTP status codes
- ✅ Global exception handling

---

## 🏗 Architecture

The application follows a **layered architecture** pattern:

```
┌─────────────────────────────────────────┐
│          Controller Layer               │  ← REST endpoints
│   (TransactionController.java)          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          Service Layer                  │  ← Business logic
│   (TransactionService.java)             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Repository Layer                │  ← Data access
│   (TransactionRepository.java)          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        In-Memory Storage                │  ← ConcurrentHashMap
│   (transactions + accountBalances)      │
└─────────────────────────────────────────┘
```

### Key Design Decisions

1. **Layered Architecture**: Separation of concerns with Controller → Service → Repository layers
2. **In-Memory Storage**: Using `ConcurrentHashMap` for thread-safe operations
3. **DTOs**: Separate Data Transfer Objects for API responses
4. **Global Exception Handler**: Centralized error handling with `@RestControllerAdvice`
5. **Bean Validation**: Jakarta validation annotations for automatic input validation
6. **Lombok**: Reduces boilerplate code for models and DTOs

---

## 🛠 Technology Stack

| Component           | Technology                    |
|---------------------|-------------------------------|
| Language            | Java 17                       |
| Framework           | Spring Boot 3.2.1             |
| Build Tool          | Gradle 8.10                   |
| Validation          | Jakarta Validation API        |
| Code Generation     | Lombok                        |
| Storage             | In-Memory (ConcurrentHashMap) |

---

## 📁 Project Structure

```
homework-1/
├── build.gradle                     # Gradle build configuration
├── settings.gradle                  # Gradle settings
├── gradlew                          # Gradle wrapper (Unix)
├── gradlew.bat                      # Gradle wrapper (Windows)
├── gradle/wrapper/                  # Gradle wrapper files
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
├── HOWTORUN.md                      # Setup and run instructions
│
├── src/main/java/com/banking/transactions/
│   ├── TransactionsApiApplication.java    # Main Spring Boot application
│   │
│   ├── controller/
│   │   └── TransactionController.java     # REST API endpoints
│   │
│   ├── service/
│   │   └── TransactionService.java        # Business logic
│   │
│   ├── repository/
│   │   └── TransactionRepository.java     # Data access layer
│   │
│   ├── model/
│   │   └── Transaction.java               # Transaction entity
│   │
│   ├── dto/
│   │   ├── AccountBalanceResponse.java    # Balance response DTO
│   │   └── ErrorResponse.java             # Error response DTO
│   │
│   └── exception/
│       ├── ResourceNotFoundException.java # Custom exception
│       └── GlobalExceptionHandler.java    # Exception handler
│
├── src/main/resources/
│   └── application.properties       # Application configuration
│
├── src/test/java/                   # Unit tests
│   └── com/banking/transactions/
│       ├── TransactionsApiApplicationTest.java
│       ├── controller/TransactionControllerTest.java
│       ├── service/TransactionServiceTest.java
│       └── repository/TransactionRepositoryTest.java
│
└── demo/
    ├── run.sh                       # Script to run the application
    ├── requests.sh                  # Sample API requests script
    ├── test.sh                      # Script to run tests
    ├── sample-requests.http         # HTTP requests (VS Code/IntelliJ)
    └── sample-data/                 # Sample data files
        ├── sample-data.json
        ├── deposits.json
        └── transfers.json
```

---

## 🚀 Quick Start

### Prerequisites
- Java 17 or higher
- Maven 3.6+

### Run the Application

```bash
# Option 1: Using the run script
cd homework-1
chmod +x demo/run.sh
./demo/run.sh

# Option 2: Using Gradle directly
./gradlew bootRun

# Option 3: Build and run JAR
./gradlew clean build
java -jar build/libs/transactions-api-1.0.0.jar
```

The API will be available at `http://localhost:8080/api`

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8080/api
```

### Endpoints

| Method | Endpoint                           | Description                    |
|--------|------------------------------------|--------------------------------|
| POST   | `/transactions`                    | Create a new transaction       |
| GET    | `/transactions`                    | Get all transactions           |
| GET    | `/transactions/{id}`               | Get transaction by ID          |
| GET    | `/accounts/{accountId}/balance`    | Get account balance            |

### Transaction Model

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fromAccount": "ACC-12345",
  "toAccount": "ACC-67890",
  "amount": 100.50,
  "currency": "USD",
  "type": "TRANSFER",
  "timestamp": "2026-02-03T10:30:00Z",
  "status": "completed"
}
```

### Transaction Types (Enum)
- `DEPOSIT` - Add funds to an account
- `WITHDRAWAL` - Remove funds from an account
- `TRANSFER` - Move funds between accounts

### Status Codes
- `200 OK` - Successful GET request
- `201 Created` - Successful POST request
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 🧪 Testing

### Using the Test Script

```bash
chmod +x demo/requests.sh
./demo/requests.sh
```

### Run Unit Tests

```bash
./gradlew test
```

View detailed test report:
```bash
open build/reports/tests/test/index.html
```

### Using curl

```bash
# Create a transaction
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.50,
    "currency": "USD",
    "type": "TRANSFER"
  }'

# Get all transactions
curl http://localhost:8080/api/transactions

# Get account balance
curl http://localhost:8080/api/accounts/ACC-12345/balance
```

### Using HTTP Client
Open `demo/sample-requests.http` in VS Code (with REST Client extension) or IntelliJ IDEA and click "Send Request".

---

## 💻 Development Commands

```bash
# Clean and compile
./gradlew clean compileJava

# Run tests
./gradlew test

# Build JAR (skip tests)
./gradlew clean build -x test

# Run the application
./gradlew bootRun

# Run with specific port
./gradlew bootRun --args='--server.port=9090'

# Check dependencies
./gradlew dependencies

# View test report
open build/reports/tests/test/index.html
```

---

## 📝 Example Request/Response

### Create Transaction
**Request:**
```bash
POST /api/transactions
Content-Type: application/json

{
  "fromAccount": "ACC-12345",
  "toAccount": "ACC-67890",
  "amount": 100.50,
  "currency": "USD",
  "type": "TRANSFER"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fromAccount": "ACC-12345",
  "toAccount": "ACC-67890",
  "amount": 100.50,
  "currency": "USD",
  "type": "TRANSFER",
  "timestamp": "2026-02-03T10:30:00Z",
  "status": "completed"
}
```

### Validation Error
**Request:**
```bash
POST /api/transactions
Content-Type: application/json

{
  "fromAccount": "ACC-12345",
  "toAccount": "ACC-67890",
  "amount": -100.00,
  "currency": "USD",
  "type": "TRANSFER"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "amount",
      "message": "amount must be positive"
    }
  ]
}
```

---

## 📄 License

This project is created for educational purposes as part of the AI Coding Partner Homework assignment.

---

**Built with ❤️ using AI-assisted development**
