package com.banking.transactions.service;

import com.banking.transactions.dto.AccountBalanceResponse;
import com.banking.transactions.dto.AccountSummaryResponse;
import com.banking.transactions.exception.ResourceNotFoundException;
import com.banking.transactions.model.Transaction;
import com.banking.transactions.model.TransactionType;
import com.banking.transactions.repository.TransactionRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;

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

    public List<Transaction> getFilteredTransactions(String accountId, TransactionType type, Instant from, Instant to) {
        return repository.findByFilters(accountId, type, from, to);
    }

    public AccountSummaryResponse getAccountSummary(String accountId) {
        List<Transaction> transactions = repository.findByAccountId(accountId);

        BigDecimal totalDeposits = transactions.stream()
                .filter(t -> t.getType() == TransactionType.DEPOSIT && t.getToAccount().equals(accountId))
                .map(Transaction::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal totalWithdrawals = transactions.stream()
                .filter(t -> t.getType() == TransactionType.WITHDRAWAL && t.getFromAccount().equals(accountId))
                .map(Transaction::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // For transfers: add incoming transfers as deposits, outgoing as withdrawals
        BigDecimal incomingTransfers = transactions.stream()
                .filter(t -> t.getType() == TransactionType.TRANSFER && t.getToAccount().equals(accountId))
                .map(Transaction::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal outgoingTransfers = transactions.stream()
                .filter(t -> t.getType() == TransactionType.TRANSFER && t.getFromAccount().equals(accountId))
                .map(Transaction::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        totalDeposits = totalDeposits.add(incomingTransfers);
        totalWithdrawals = totalWithdrawals.add(outgoingTransfers);

        Instant mostRecentDate = transactions.stream()
                .map(Transaction::getTimestamp)
                .filter(java.util.Objects::nonNull)
                .max(Instant::compareTo)
                .orElse(null);

        return AccountSummaryResponse.builder()
                .accountId(accountId)
                .totalDeposits(totalDeposits)
                .totalWithdrawals(totalWithdrawals)
                .transactionCount(transactions.size())
                .mostRecentTransactionDate(mostRecentDate)
                .build();
    }

    public String exportTransactionsToCsv() {
        List<Transaction> transactions = repository.findAll();

        StringBuilder csv = new StringBuilder();
        csv.append("id,fromAccount,toAccount,amount,currency,type,timestamp,status\n");

        String rows = transactions.stream()
                .map(this::transactionToCsvRow)
                .collect(Collectors.joining("\n"));

        csv.append(rows);
        return csv.toString();
    }

    private String transactionToCsvRow(Transaction t) {
        return String.join(",",
                escapeCsvField(t.getId()),
                escapeCsvField(t.getFromAccount()),
                escapeCsvField(t.getToAccount()),
                t.getAmount() != null ? t.getAmount().toString() : "",
                escapeCsvField(t.getCurrency()),
                t.getType() != null ? t.getType().name() : "",
                t.getTimestamp() != null ? t.getTimestamp().toString() : "",
                escapeCsvField(t.getStatus())
        );
    }

    private String escapeCsvField(String field) {
        if (field == null) {
            return "";
        }
        if (field.contains(",") || field.contains("\"") || field.contains("\n")) {
            return "\"" + field.replace("\"", "\"\"") + "\"";
        }
        return field;
    }
}
