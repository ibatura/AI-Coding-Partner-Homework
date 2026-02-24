package com.banking.transactions.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.Currency;
import java.util.Set;

public class CurrencyValidator implements ConstraintValidator<ValidCurrency, String> {

    private static final Set<String> VALID_CURRENCIES = Set.of(
        "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
        "CNY", "INR", "BRL", "RUB", "KRW", "MXN", "SGD", "HKD",
        "NOK", "SEK", "DKK", "PLN", "ZAR", "THB", "MYR", "IDR"
    );

    @Override
    public void initialize(ValidCurrency constraintAnnotation) {
        ConstraintValidator.super.initialize(constraintAnnotation);
    }

    @Override
    public boolean isValid(String currency, ConstraintValidatorContext context) {
        if (currency == null || currency.isBlank()) {
            return false;
        }

        // Check against our predefined list of common currencies
        if (VALID_CURRENCIES.contains(currency.toUpperCase())) {
            return true;
        }

        // Also validate using Java's Currency class for ISO 4217 codes
        try {
            Currency.getInstance(currency.toUpperCase());
            return true;
        } catch (IllegalArgumentException e) {
            return false;
        }
    }
}
