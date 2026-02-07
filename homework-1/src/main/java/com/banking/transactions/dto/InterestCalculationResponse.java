package com.banking.transactions.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InterestCalculationResponse {
    private String accountId;
    private BigDecimal principal;
    private BigDecimal rate;
    private Integer days;
    private BigDecimal interest;
    private BigDecimal finalBalance;
    private String currency;
}
