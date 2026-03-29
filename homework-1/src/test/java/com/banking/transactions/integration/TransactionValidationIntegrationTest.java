package com.banking.transactions.integration;

import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class TransactionValidationIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void testValidTransaction_Success() throws Exception {
        Transaction transaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.50"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        mockMvc.perform(post("/api/transactions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(transaction)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.fromAccount").value("ACC-12345"))
                .andExpect(jsonPath("$.toAccount").value("ACC-67890"))
                .andExpect(jsonPath("$.amount").value(100.50))
                .andExpect(jsonPath("$.currency").value("USD"));
    }

    @Test
    void testInvalidAmount_Negative() throws Exception {
        Transaction transaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("-100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        mockMvc.perform(post("/api/transactions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(transaction)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation failed"))
                .andExpect(jsonPath("$.details[0].field").value("amount"))
                .andExpect(jsonPath("$.details[0].message").value("Amount must be a positive number"));
    }

    @Test
    void testInvalidAmount_TooManyDecimals() throws Exception {
        Transaction transaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.123"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        mockMvc.perform(post("/api/transactions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(transaction)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation failed"))
                .andExpect(jsonPath("$.details[0].field").value("amount"))
                .andExpect(jsonPath("$.details[0].message").value("Amount must have maximum 2 decimal places"));
    }

    @Test
    void testInvalidAccountNumber_WrongFormat() throws Exception {
        Transaction transaction = Transaction.builder()
                .fromAccount("INVALID123")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        mockMvc.perform(post("/api/transactions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(transaction)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation failed"))
                .andExpect(jsonPath("$.details[?(@.field == 'fromAccount')]").exists());
    }

    @Test
    void testInvalidCurrency() throws Exception {
        Transaction transaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("XYZ")
                .type(TransactionType.TRANSFER)
                .build();

        mockMvc.perform(post("/api/transactions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(transaction)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation failed"))
                .andExpect(jsonPath("$.details[?(@.field == 'currency')]").exists());
    }

    @Test
    void testMultipleValidationErrors() throws Exception {
        Transaction transaction = Transaction.builder()
                .fromAccount("INVALID")
                .toAccount("ALSO-INVALID")
                .amount(new BigDecimal("-100.123"))
                .currency("NOTREAL")
                .type(TransactionType.TRANSFER)
                .build();

        mockMvc.perform(post("/api/transactions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(transaction)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation failed"))
                .andExpect(jsonPath("$.details").isArray())
                .andExpect(jsonPath("$.details.length()").value(4)); // All 4 fields should have errors
    }

    @Test
    void testValidCurrencies() throws Exception {
        String[] validCurrencies = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"};

        for (String currency : validCurrencies) {
            Transaction transaction = Transaction.builder()
                    .fromAccount("ACC-12345")
                    .toAccount("ACC-67890")
                    .amount(new BigDecimal("100.00"))
                    .currency(currency)
                    .type(TransactionType.TRANSFER)
                    .build();

            mockMvc.perform(post("/api/transactions")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(transaction)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.currency").value(currency));
        }
    }

    @Test
    void testValidAccountFormats() throws Exception {
        String[] validAccounts = {"ACC-12345", "ACC-ABCDE", "ACC-A1B2C", "ACC-ab123"};

        for (String account : validAccounts) {
            Transaction transaction = Transaction.builder()
                    .fromAccount(account)
                    .toAccount("ACC-99999")
                    .amount(new BigDecimal("100.00"))
                    .currency("USD")
                    .type(TransactionType.TRANSFER)
                    .build();

            mockMvc.perform(post("/api/transactions")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(transaction)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.fromAccount").value(account));
        }
    }
}
