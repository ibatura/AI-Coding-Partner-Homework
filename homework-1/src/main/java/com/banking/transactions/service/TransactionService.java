package com.banking.transactions.service;

import com.banking.transactions.dto.AccountBalanceResponse;
import com.banking.transactions.exception.ResourceNotFoundException;
import com.banking.transactions.model.Transaction;
import com.banking.transactions.repository.TransactionRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

@Service
public class TransactionService {

    private final TransactionRepository repository;

    public TransactionService(TransactionRepository repository) {
        this.repository = repository;
    }

    public Transaction createTransaction(Transaction transaction) {
        transaction.setTimestamp(Instant.now());
        transaction.setStatus("completed");
        return repository.save(transaction);
    }

    public List<Transaction> getAllTransactions() {
        return repository.findAll();
    }

    public Transaction getTransactionById(String id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Transaction not found with id: " + id));
    }

    public AccountBalanceResponse getAccountBalance(String accountId) {
        BigDecimal balance = repository.getAccountBalance(accountId);
        // Default currency to USD for simplicity
        return AccountBalanceResponse.builder()
                .accountId(accountId)
                .balance(balance)
                .currency("USD")
                .build();
    }

    public List<Transaction> getTransactionsByAccountId(String accountId) {
        return repository.findByAccountId(accountId);
    }
}
