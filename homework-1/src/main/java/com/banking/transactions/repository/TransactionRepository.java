package com.banking.transactions.repository;

import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Repository
public class TransactionRepository {

    private final Map<String, Transaction> transactions = new ConcurrentHashMap<>();
    private final Map<String, BigDecimal> accountBalances = new ConcurrentHashMap<>();

    public Transaction save(Transaction transaction) {
        String id = UUID.randomUUID().toString();
        transaction.setId(id);
        transactions.put(id, transaction);
        updateAccountBalance(transaction);
        return transaction;
    }

    public Optional<Transaction> findById(String id) {
        return Optional.ofNullable(transactions.get(id));
    }

    public List<Transaction> findAll() {
        return new ArrayList<>(transactions.values());
    }

    public BigDecimal getAccountBalance(String accountId) {
        return accountBalances.getOrDefault(accountId, BigDecimal.ZERO);
    }

    public List<Transaction> findByAccountId(String accountId) {
        return transactions.values().stream()
                .filter(t -> t.getFromAccount().equals(accountId) || t.getToAccount().equals(accountId))
                .collect(Collectors.toList());
    }

    public List<Transaction> findByFilters(String accountId, TransactionType type, Instant from, Instant to) {
        Stream<Transaction> stream = transactions.values().stream();

        // Filter by account ID (either fromAccount or toAccount)
        if (accountId != null && !accountId.isEmpty()) {
            stream = stream.filter(t ->
                t.getFromAccount().equals(accountId) || t.getToAccount().equals(accountId)
            );
        }

        // Filter by transaction type
        if (type != null) {
            stream = stream.filter(t -> t.getType() == type);
        }

        // Filter by date range
        if (from != null) {
            stream = stream.filter(t -> t.getTimestamp() != null && !t.getTimestamp().isBefore(from));
        }

        if (to != null) {
            stream = stream.filter(t -> t.getTimestamp() != null && !t.getTimestamp().isAfter(to));
        }

        return stream.collect(Collectors.toList());
    }

    public void clear() {
        transactions.clear();
        accountBalances.clear();
    }

    private void updateAccountBalance(Transaction transaction) {
        TransactionType type = transaction.getType();
        BigDecimal amount = transaction.getAmount();

        switch (type) {
            case DEPOSIT:
                accountBalances.merge(transaction.getToAccount(), amount, BigDecimal::add);
                break;
            case WITHDRAWAL:
                accountBalances.merge(transaction.getFromAccount(), amount, BigDecimal::subtract);
                break;
            case TRANSFER:
                accountBalances.merge(transaction.getFromAccount(), amount, BigDecimal::subtract);
                accountBalances.merge(transaction.getToAccount(), amount, BigDecimal::add);
                break;
        }
    }
}
