package com.banking.transactions.integration;

import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import com.banking.transactions.repository.TransactionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest
@AutoConfigureMockMvc
public class TransactionFilteringIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private TransactionRepository repository;

    @Autowired
    private ObjectMapper objectMapper;

    private Instant now;
    private Instant yesterday;
    private Instant twoDaysAgo;
    private Instant tomorrow;

    @BeforeEach
    void setUp() {
        // Clear the repository before each test
        repository.clear();

        // Set up time references
        now = Instant.now();
        yesterday = now.minus(1, ChronoUnit.DAYS);
        twoDaysAgo = now.minus(2, ChronoUnit.DAYS);
        tomorrow = now.plus(1, ChronoUnit.DAYS);

        // Create test transactions
        createTestTransaction("ACC-001", "ACC-002", TransactionType.TRANSFER, new BigDecimal("100.00"), twoDaysAgo);
        createTestTransaction("ACC-001", "ACC-003", TransactionType.TRANSFER, new BigDecimal("50.00"), yesterday);
        createTestTransaction("ACC-002", "ACC-004", TransactionType.DEPOSIT, new BigDecimal("200.00"), yesterday);
        createTestTransaction("ACC-003", "ACC-005", TransactionType.WITHDRAWAL, new BigDecimal("75.00"), now);
        createTestTransaction("ACC-001", "ACC-004", TransactionType.TRANSFER, new BigDecimal("150.00"), now);
    }

    private void createTestTransaction(String from, String to, TransactionType type, BigDecimal amount, Instant timestamp) {
        Transaction transaction = Transaction.builder()
                .fromAccount(from)
                .toAccount(to)
                .type(type)
                .amount(amount)
                .currency("USD")
                .timestamp(timestamp)
                .status("completed")
                .build();
        repository.save(transaction);
    }

    @Test
    void shouldReturnAllTransactionsWhenNoFiltersProvided() throws Exception {
        mockMvc.perform(get("/api/transactions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(5)));
    }

    @Test
    void shouldFilterTransactionsByAccountId() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("accountId", "ACC-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)))
                .andExpect(jsonPath("$[*].fromAccount", everyItem(is("ACC-001"))))
                .andExpect(jsonPath("$[*].toAccount", hasItem(is("ACC-002"))))
                .andExpect(jsonPath("$[*].toAccount", hasItem(is("ACC-003"))))
                .andExpect(jsonPath("$[*].toAccount", hasItem(is("ACC-004"))));
    }

    @Test
    void shouldFilterTransactionsByType() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("type", "TRANSFER"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)))
                .andExpect(jsonPath("$[*].type", everyItem(is("TRANSFER"))));

        mockMvc.perform(get("/api/transactions")
                        .param("type", "DEPOSIT"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].type", is("DEPOSIT")));

        mockMvc.perform(get("/api/transactions")
                        .param("type", "WITHDRAWAL"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].type", is("WITHDRAWAL")));
    }

    @Test
    void shouldFilterTransactionsByDateRange() throws Exception {
        // Filter from yesterday to tomorrow
        mockMvc.perform(get("/api/transactions")
                        .param("from", yesterday.toString())
                        .param("to", tomorrow.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(4))); // Excludes the transaction from 2 days ago

        // Filter only today
        mockMvc.perform(get("/api/transactions")
                        .param("from", now.minus(1, ChronoUnit.HOURS).toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)));
    }

    @Test
    void shouldFilterTransactionsByFromDateOnly() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("from", yesterday.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(4))); // Excludes transaction from 2 days ago
    }

    @Test
    void shouldFilterTransactionsByToDateOnly() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("to", yesterday.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3))); // Includes transactions up to yesterday
    }

    @Test
    void shouldCombineMultipleFilters_AccountIdAndType() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("accountId", "ACC-001")
                        .param("type", "TRANSFER"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)))
                .andExpect(jsonPath("$[*].type", everyItem(is("TRANSFER"))));
    }

    @Test
    void shouldCombineMultipleFilters_AccountIdAndDateRange() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("accountId", "ACC-001")
                        .param("from", yesterday.toString())
                        .param("to", tomorrow.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2))); // Only yesterday and today transactions
    }

    @Test
    void shouldCombineMultipleFilters_TypeAndDateRange() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("type", "TRANSFER")
                        .param("from", yesterday.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2))); // Transfers from yesterday and today
    }

    @Test
    void shouldCombineAllFilters() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("accountId", "ACC-001")
                        .param("type", "TRANSFER")
                        .param("from", twoDaysAgo.toString())
                        .param("to", yesterday.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2))); // Transfers from ACC-001 in the date range
    }

    @Test
    void shouldReturnEmptyListWhenNoTransactionsMatchFilters() throws Exception {
        mockMvc.perform(get("/api/transactions")
                        .param("accountId", "ACC-999"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));

        mockMvc.perform(get("/api/transactions")
                        .param("type", "DEPOSIT")
                        .param("accountId", "ACC-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void shouldFilterByAccountIdForBothFromAndToAccounts() throws Exception {
        // ACC-002 is toAccount in one transaction and fromAccount in another
        mockMvc.perform(get("/api/transactions")
                        .param("accountId", "ACC-002"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)));
    }

    @Test
    void shouldHandleInvalidTransactionType() throws Exception {
        // Spring returns 400 or 500 for invalid enum values depending on configuration
        // We just verify it doesn't return success
        mockMvc.perform(get("/api/transactions")
                        .param("type", "INVALID_TYPE"))
                .andExpect(result -> assertTrue(result.getResponse().getStatus() >= 400));
    }

    @Test
    void shouldHandleInvalidDateFormat() throws Exception {
        // Spring returns 400 or 500 for invalid date format depending on configuration
        // We just verify it doesn't return success
        mockMvc.perform(get("/api/transactions")
                        .param("from", "invalid-date"))
                .andExpect(result -> assertTrue(result.getResponse().getStatus() >= 400));
    }

    @Test
    void shouldHandleDateRangeWhereFromIsAfterTo() throws Exception {
        // This should return empty list as the date range is invalid
        mockMvc.perform(get("/api/transactions")
                        .param("from", tomorrow.toString())
                        .param("to", yesterday.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }
}
