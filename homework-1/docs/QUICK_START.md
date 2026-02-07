# 🚀 Quick Start Guide

## Get the API Running in 3 Steps

### Step 1: Navigate to the project
```bash
cd /Users/i.batura/Projects/mine/AI-Coding-Partner-Homework/homework-1
```

### Step 2: Run the application
```bash
mvn spring-boot:run
```

### Step 3: Test it!
Open another terminal and run:
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-12345",
    "toAccount": "ACC-67890",
    "amount": 100.50,
    "currency": "USD",
    "type": "transfer"
  }'
```

---

## 📦 Complete File Tree

```
homework-1/
├── pom.xml
├── .gitignore
├── README.md
├── HOWTORUN.md
├── PROJECT_SUMMARY.md
├── QUICK_START.md (this file)
│
├── src/
│   ├── main/
│   │   ├── java/com/banking/transactions/
│   │   │   ├── TransactionsApiApplication.java
│   │   │   ├── controller/
│   │   │   │   └── TransactionController.java
│   │   │   ├── service/
│   │   │   │   └── TransactionService.java
│   │   │   ├── repository/
│   │   │   │   └── TransactionRepository.java
│   │   │   ├── model/
│   │   │   │   └── Transaction.java
│   │   │   ├── dto/
│   │   │   │   ├── AccountBalanceResponse.java
│   │   │   │   └── ErrorResponse.java
│   │   │   └── exception/
│   │   │       ├── ResourceNotFoundException.java
│   │   │       └── GlobalExceptionHandler.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
│       └── (tests can be added here)
│
└── demo/
    ├── run.sh
    ├── sample-requests.http
    ├── sample-requests.sh
    └── sample-data.json
```

---

## ✅ API Endpoints

| Method | Endpoint | Example |
|--------|----------|---------|
| POST | `/api/transactions` | Create transaction |
| GET | `/api/transactions` | List all transactions |
| GET | `/api/transactions/{id}` | Get transaction by ID |
| GET | `/api/accounts/{accountId}/balance` | Get account balance |

---

## 🧪 Quick Test Commands

```bash
# 1. Create a deposit
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-00000","toAccount":"ACC-12345","amount":1000.00,"currency":"USD","type":"deposit"}'

# 2. Create a transfer
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"fromAccount":"ACC-12345","toAccount":"ACC-67890","amount":250.75,"currency":"USD","type":"transfer"}'

# 3. Get all transactions
curl http://localhost:8080/api/transactions

# 4. Get balance for ACC-12345
curl http://localhost:8080/api/accounts/ACC-12345/balance

# 5. Get balance for ACC-67890
curl http://localhost:8080/api/accounts/ACC-67890/balance
```

---

## 📖 Need More Details?

- **README.md** - Complete documentation with architecture
- **HOWTORUN.md** - Detailed setup and troubleshooting
- **PROJECT_SUMMARY.md** - Project overview and checklist
- **TASKS.md** - Original assignment requirements

---

**That's it! You're ready to go! 🎉**
