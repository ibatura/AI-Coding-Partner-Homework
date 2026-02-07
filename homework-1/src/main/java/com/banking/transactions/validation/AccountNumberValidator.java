package com.banking.transactions.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.regex.Pattern;

public class AccountNumberValidator implements ConstraintValidator<ValidAccountNumber, String> {

    // Pattern: ACC- followed by exactly 5 alphanumeric characters
    private static final Pattern ACCOUNT_PATTERN = Pattern.compile("^ACC-[A-Za-z0-9]{5}$");

    @Override
    public void initialize(ValidAccountNumber constraintAnnotation) {
        ConstraintValidator.super.initialize(constraintAnnotation);
    }

    @Override
    public boolean isValid(String accountNumber, ConstraintValidatorContext context) {
        if (accountNumber == null || accountNumber.isBlank()) {
            return false;
        }

        return ACCOUNT_PATTERN.matcher(accountNumber).matches();
    }
}
