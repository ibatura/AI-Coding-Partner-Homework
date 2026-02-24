package com.banking.transactions.model;

import com.banking.transactions.validation.ValidAccountNumber;
import com.banking.transactions.validation.ValidAmount;
import com.banking.transactions.validation.ValidCurrency;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
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
    @ValidAccountNumber
    private String fromAccount;

    @NotBlank(message = "toAccount is required")
    @ValidAccountNumber
    private String toAccount;

    @NotNull(message = "amount is required")
    @ValidAmount
    private BigDecimal amount;

    @NotBlank(message = "currency is required")
    @ValidCurrency
    private String currency;

    @NotNull(message = "type is required")
    private TransactionType type; // DEPOSIT | WITHDRAWAL | TRANSFER

    private Instant timestamp;

    @Builder.Default
    private String status = "pending"; // pending | completed | failed
}
