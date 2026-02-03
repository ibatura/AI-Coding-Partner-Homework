package com.banking.transactions.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
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
public class Transaction {

    private String id;

    @NotBlank(message = "fromAccount is required")
    private String fromAccount;

    @NotBlank(message = "toAccount is required")
    private String toAccount;

    @NotNull(message = "amount is required")
    @Positive(message = "amount must be positive")
    private BigDecimal amount;

    @NotBlank(message = "currency is required")
    private String currency;

    @NotNull(message = "type is required")
    private TransactionType type; // DEPOSIT | WITHDRAWAL | TRANSFER

    private Instant timestamp;

    @Builder.Default
    private String status = "pending"; // pending | completed | failed
}
