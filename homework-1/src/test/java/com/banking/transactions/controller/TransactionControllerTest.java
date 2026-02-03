package com.banking.transactions.controller;

import com.banking.transactions.dto.AccountBalanceResponse;
import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import com.banking.transactions.service.TransactionService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TransactionController.class)
public class TransactionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private TransactionService transactionService;

    @Test
    public void testCreateTransaction_Success() throws Exception {
        Transaction transaction = Transaction.builder()
                .id("test-id-123")
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.50"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .timestamp(Instant.now())
                .status("completed")
                .build();

        when(transactionService.createTransaction(any(Transaction.class)))
                .thenReturn(transaction);

        mockMvc.perform(post("/api/transactions")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"fromAccount\":\"ACC-12345\",\"toAccount\":\"ACC-67890\",\"amount\":100.50,\"currency\":\"USD\",\"type\":\"TRANSFER\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("test-id-123"))
                .andExpect(jsonPath("$.fromAccount").value("ACC-12345"))
                .andExpect(jsonPath("$.toAccount").value("ACC-67890"))
                .andExpect(jsonPath("$.amount").value(100.50))
                .andExpect(jsonPath("$.currency").value("USD"))
                .andExpect(jsonPath("$.type").value("TRANSFER"))
                .andExpect(jsonPath("$.status").value("completed"));
    }

    @Test
    public void testCreateTransaction_NegativeAmount_BadRequest() throws Exception {
        mockMvc.perform(post("/api/transactions")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"fromAccount\":\"ACC-12345\",\"toAccount\":\"ACC-67890\",\"amount\":-100.50,\"currency\":\"USD\",\"type\":\"TRANSFER\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation failed"));
    }

    @Test
    public void testCreateTransaction_MissingRequiredFields_BadRequest() throws Exception {
        mockMvc.perform(post("/api/transactions")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"fromAccount\":\"ACC-12345\",\"amount\":100.50}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    public void testGetAllTransactions_Success() throws Exception {
        Transaction transaction1 = Transaction.builder()
                .id("test-id-1")
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .timestamp(Instant.now())
                .status("completed")
                .build();

        Transaction transaction2 = Transaction.builder()
                .id("test-id-2")
                .fromAccount("ACC-11111")
                .toAccount("ACC-22222")
                .amount(new BigDecimal("200.00"))
                .currency("EUR")
                .type(TransactionType.DEPOSIT)
                .timestamp(Instant.now())
                .status("completed")
                .build();

        List<Transaction> transactions = Arrays.asList(transaction1, transaction2);
        when(transactionService.getAllTransactions()).thenReturn(transactions);

        mockMvc.perform(get("/api/transactions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("test-id-1"))
                .andExpect(jsonPath("$[0].amount").value(100.00))
                .andExpect(jsonPath("$[1].id").value("test-id-2"))
                .andExpect(jsonPath("$[1].amount").value(200.00));
    }

    @Test
    public void testGetTransactionById_Success() throws Exception {
        Transaction transaction = Transaction.builder()
                .id("test-id-123")
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.50"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .timestamp(Instant.now())
                .status("completed")
                .build();

        when(transactionService.getTransactionById(eq("test-id-123")))
                .thenReturn(transaction);

        mockMvc.perform(get("/api/transactions/test-id-123"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("test-id-123"))
                .andExpect(jsonPath("$.fromAccount").value("ACC-12345"));
    }

    @Test
    public void testGetAccountBalance_Success() throws Exception {
        AccountBalanceResponse balance = AccountBalanceResponse.builder()
                .accountId("ACC-12345")
                .balance(new BigDecimal("899.50"))
                .currency("USD")
                .build();

        when(transactionService.getAccountBalance(eq("ACC-12345")))
                .thenReturn(balance);

        mockMvc.perform(get("/api/accounts/ACC-12345/balance"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.accountId").value("ACC-12345"))
                .andExpect(jsonPath("$.balance").value(899.50))
                .andExpect(jsonPath("$.currency").value("USD"));
    }
}
