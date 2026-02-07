package com.banking.transactions.service;

import com.banking.transactions.dto.AccountBalanceResponse;
import com.banking.transactions.exception.ResourceNotFoundException;
import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import com.banking.transactions.repository.TransactionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class TransactionServiceTest {

    @Mock
    private TransactionRepository repository;

    @InjectMocks
    private TransactionService transactionService;

    private Transaction sampleTransaction;

    @BeforeEach
    public void setUp() {
        sampleTransaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.50"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();
    }

    @Test
    public void testCreateTransaction_Success() {
        when(repository.save(any(Transaction.class))).thenAnswer(invocation -> {
            Transaction arg = invocation.getArgument(0);
            arg.setId("generated-id");
            return arg;
        });

        Transaction result = transactionService.createTransaction(sampleTransaction);

        assertNotNull(result);
        assertEquals("generated-id", result.getId());
        assertEquals("completed", result.getStatus());
        assertNotNull(result.getTimestamp());
        verify(repository, times(1)).save(any(Transaction.class));
    }

    @Test
    public void testGetAllTransactions_Success() {
        List<Transaction> transactions = Arrays.asList(
                Transaction.builder().id("id-1").build(),
                Transaction.builder().id("id-2").build()
        );

        when(repository.findAll()).thenReturn(transactions);

        List<Transaction> result = transactionService.getAllTransactions();

        assertNotNull(result);
        assertEquals(2, result.size());
        verify(repository, times(1)).findAll();
    }

    @Test
    public void testGetTransactionById_Success() {
        Transaction transaction = Transaction.builder()
                .id("test-id")
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.50"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        when(repository.findById("test-id")).thenReturn(Optional.of(transaction));

        Transaction result = transactionService.getTransactionById("test-id");

        assertNotNull(result);
        assertEquals("test-id", result.getId());
        verify(repository, times(1)).findById("test-id");
    }

    @Test
    public void testGetTransactionById_NotFound() {
        when(repository.findById("non-existent-id")).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> {
            transactionService.getTransactionById("non-existent-id");
        });

        verify(repository, times(1)).findById("non-existent-id");
    }

    @Test
    public void testGetAccountBalance_Success() {
        when(repository.getAccountBalance("ACC-12345"))
                .thenReturn(new BigDecimal("1000.00"));

        AccountBalanceResponse result = transactionService.getAccountBalance("ACC-12345");

        assertNotNull(result);
        assertEquals("ACC-12345", result.getAccountId());
        assertEquals(new BigDecimal("1000.00"), result.getBalance());
        assertEquals("USD", result.getCurrency());
        verify(repository, times(1)).getAccountBalance("ACC-12345");
    }

    @Test
    public void testGetTransactionsByAccountId_Success() {
        List<Transaction> transactions = Arrays.asList(
                Transaction.builder().id("id-1").fromAccount("ACC-12345").build(),
                Transaction.builder().id("id-2").toAccount("ACC-12345").build()
        );

        when(repository.findByAccountId("ACC-12345")).thenReturn(transactions);

        List<Transaction> result = transactionService.getTransactionsByAccountId("ACC-12345");

        assertNotNull(result);
        assertEquals(2, result.size());
        verify(repository, times(1)).findByAccountId("ACC-12345");
    }
}
