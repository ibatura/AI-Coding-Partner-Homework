package com.banking.transactions.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AccountSummaryResponse {
    private String accountId;
    private BigDecimal totalDeposits;
    private BigDecimal totalWithdrawals;
    private Integer transactionCount;
    private Instant mostRecentTransactionDate;
}
