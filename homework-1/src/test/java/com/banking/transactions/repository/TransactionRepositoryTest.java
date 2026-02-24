package com.banking.transactions.repository;

import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

public class TransactionRepositoryTest {

    private TransactionRepository repository;

    @BeforeEach
    public void setUp() {
        repository = new TransactionRepository();
    }

    @Test
    public void testSave_GeneratesIdAndReturnsTransaction() {
        Transaction transaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        Transaction saved = repository.save(transaction);

        assertNotNull(saved.getId());
        assertEquals("ACC-12345", saved.getFromAccount());
        assertEquals("ACC-67890", saved.getToAccount());
    }

    @Test
    public void testFindById_Success() {
        Transaction transaction = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        Transaction saved = repository.save(transaction);
        Optional<Transaction> found = repository.findById(saved.getId());

        assertTrue(found.isPresent());
        assertEquals(saved.getId(), found.get().getId());
    }

    @Test
    public void testFindById_NotFound() {
        Optional<Transaction> found = repository.findById("non-existent-id");
        assertFalse(found.isPresent());
    }

    @Test
    public void testFindAll_ReturnsAllTransactions() {
        Transaction transaction1 = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        Transaction transaction2 = Transaction.builder()
                .fromAccount("ACC-11111")
                .toAccount("ACC-22222")
                .amount(new BigDecimal("200.00"))
                .currency("EUR")
                .type(TransactionType.DEPOSIT)
                .build();

        repository.save(transaction1);
        repository.save(transaction2);

        List<Transaction> all = repository.findAll();

        assertEquals(2, all.size());
    }

    @Test
    public void testGetAccountBalance_Deposit() {
        Transaction deposit = Transaction.builder()
                .fromAccount("ACC-00000")
                .toAccount("ACC-12345")
                .amount(new BigDecimal("1000.00"))
                .currency("USD")
                .type(TransactionType.DEPOSIT)
                .build();

        repository.save(deposit);

        BigDecimal balance = repository.getAccountBalance("ACC-12345");
        assertEquals(new BigDecimal("1000.00"), balance);
    }

    @Test
    public void testGetAccountBalance_Withdrawal() {
        // First deposit
        Transaction deposit = Transaction.builder()
                .fromAccount("ACC-00000")
                .toAccount("ACC-12345")
                .amount(new BigDecimal("1000.00"))
                .currency("USD")
                .type(TransactionType.DEPOSIT)
                .build();
        repository.save(deposit);

        // Then withdrawal
        Transaction withdrawal = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-00000")
                .amount(new BigDecimal("200.00"))
                .currency("USD")
                .type(TransactionType.WITHDRAWAL)
                .build();
        repository.save(withdrawal);

        BigDecimal balance = repository.getAccountBalance("ACC-12345");
        assertEquals(new BigDecimal("800.00"), balance);
    }

    @Test
    public void testGetAccountBalance_Transfer() {
        // Deposit to first account
        Transaction deposit = Transaction.builder()
                .fromAccount("ACC-00000")
                .toAccount("ACC-12345")
                .amount(new BigDecimal("1000.00"))
                .currency("USD")
                .type(TransactionType.DEPOSIT)
                .build();
        repository.save(deposit);

        // Transfer to second account
        Transaction transfer = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("300.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();
        repository.save(transfer);

        BigDecimal balance1 = repository.getAccountBalance("ACC-12345");
        BigDecimal balance2 = repository.getAccountBalance("ACC-67890");

        assertEquals(new BigDecimal("700.00"), balance1);
        assertEquals(new BigDecimal("300.00"), balance2);
    }

    @Test
    public void testGetAccountBalance_NoTransactions() {
        BigDecimal balance = repository.getAccountBalance("ACC-99999");
        assertEquals(BigDecimal.ZERO, balance);
    }

    @Test
    public void testFindByAccountId_Success() {
        Transaction transaction1 = Transaction.builder()
                .fromAccount("ACC-12345")
                .toAccount("ACC-67890")
                .amount(new BigDecimal("100.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        Transaction transaction2 = Transaction.builder()
                .fromAccount("ACC-11111")
                .toAccount("ACC-12345")
                .amount(new BigDecimal("200.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        Transaction transaction3 = Transaction.builder()
                .fromAccount("ACC-99999")
                .toAccount("ACC-88888")
                .amount(new BigDecimal("300.00"))
                .currency("USD")
                .type(TransactionType.TRANSFER)
                .build();

        repository.save(transaction1);
        repository.save(transaction2);
        repository.save(transaction3);

        List<Transaction> accountTransactions = repository.findByAccountId("ACC-12345");

        assertEquals(2, accountTransactions.size());
    }
}
