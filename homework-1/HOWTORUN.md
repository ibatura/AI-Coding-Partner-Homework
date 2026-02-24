# ▶️ How to Run the Banking Transactions API

This guide provides step-by-step instructions to set up and run the application.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Java Development Kit (JDK) 17 or higher**
  - Check version: `java -version`
  - Download from: https://www.oracle.com/java/technologies/downloads/

**Note:** Gradle wrapper is included - no need to install Gradle separately!

---

## 🚀 Quick Start

### Option 1: Using the Run Script (Recommended)

```bash
cd homework-1
chmod +x demo/run.sh
./demo/run.sh
```

This script will:
1. Clean any previous builds
2. Compile and package the application
3. Start the Spring Boot server

### Option 2: Using Gradle Directly

```bash
cd homework-1
./gradlew bootRun
```

### Option 3: Build JAR and Run

```bash
cd homework-1
./gradlew clean build
java -jar build/libs/transactions-api-1.0.0.jar
```

---

## ✅ Verify the Application is Running

Once started, you should see output similar to:

```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.1)

...
Started TransactionsApiApplication in X.XXX seconds
```

The API will be accessible at: **http://localhost:8080/api**

---

## 🧪 Test the API

### Using the Test Script

Run the automated test script to verify all endpoints:

```bash
chmod +x demo/requests.sh
./demo/requests.sh
```

### Run Unit Tests

```bash
./gradlew test
```

View test report:
```bash
open build/reports/tests/test/index.html
```

### Using curl Commands

#### 1. Create a deposit transaction
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "fromAccount": "ACC-00000",
    "toAccount": "ACC-12345",
    "amount": 1000.00,
    "currency": "USD",
    "type": "deposit"
  }'
```

#### 2. Get all transactions
```bash
curl http://localhost:8080/api/transactions
```

#### 3. Get account balance
```bash
curl http://localhost:8080/api/accounts/ACC-12345/balance
```

#### 4. Get specific transaction by ID
```bash
curl http://localhost:8080/api/transactions/{TRANSACTION-ID}
```
*(Replace `{TRANSACTION-ID}` with an actual ID from step 1)*

### Using HTTP Client File

If you're using **VS Code** with the REST Client extension or **IntelliJ IDEA**:

1. Open `demo/sample-requests.http`
2. Click on "Send Request" above each request
3. View the response in the panel

---

## 🛑 Stopping the Application

Press `Ctrl + C` in the terminal where the application is running.

---

## 🔧 Troubleshooting

### Port Already in Use

If port 8080 is already in use, you can change it:

**Temporary change:**
```bash
./gradlew bootRun --args='--server.port=9090'
```

**Permanent change:**
Edit `src/main/resources/application.properties`:
```properties
server.port=9090
```

### Gradle Build Errors

**Clear Gradle cache and rebuild:**
```bash
./gradlew clean build --refresh-dependencies
```

### Java Version Issues

Ensure you're using Java 17+:
```bash
java -version
```

If you have multiple Java versions, set `JAVA_HOME`:
```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

### Lombok Issues in IDE

If your IDE shows errors with Lombok annotations:

**IntelliJ IDEA:**
1. Install Lombok plugin: Settings → Plugins → Search "Lombok"
2. Enable annotation processing: Settings → Build → Compiler → Annotation Processors → Enable

**Eclipse:**
1. Download lombok.jar from https://projectlombok.org/download
2. Run: `java -jar lombok.jar`
3. Select your Eclipse installation

**VS Code:**
1. Install "Language Support for Java" extension
2. Lombok should work out of the box

---

## 📦 Building for Production

### Create an executable JAR

```bash
./gradlew clean build
```

The JAR file will be created at: `build/libs/transactions-api-1.0.0.jar`

### Run the JAR

```bash
java -jar build/libs/transactions-api-1.0.0.jar
```

### Build without tests

```bash
./gradlew clean build -x test
```

---

## 🧹 Clean Up

Remove all build artifacts:

```bash
./gradlew clean
```

---

## 📊 Additional Commands

### Check dependencies
```bash
./gradlew dependencies
```

### Update dependencies
```bash
./gradlew dependencyUpdates
```

### Run tests only
```bash
./gradlew test
```

### Compile without running
```bash
./gradlew compileJava
```

---

## 🌐 API Base URL

Once running, all endpoints are available at:

```
http://localhost:8080/api
```

### Available Endpoints:
- `POST /api/transactions` - Create transaction
- `GET /api/transactions` - List all transactions
- `GET /api/transactions/{id}` - Get transaction by ID
- `GET /api/accounts/{accountId}/balance` - Get account balance

---

## 💡 Tips

- **Hot Reload**: Spring Boot DevTools can be added for automatic restart on code changes
- **Logging**: Check application logs in the console for debugging
- **API Testing**: Use Postman, Insomnia, or the provided HTTP files for testing
- **In-Memory Storage**: All data is lost when the application stops (by design)

---

## 📞 Need Help?

- Check the **README.md** for architecture details
- Review the **TASKS.md** for requirements
- Examine the code in `src/main/java/com/banking/transactions/`

---

**Happy coding! 🎉**
