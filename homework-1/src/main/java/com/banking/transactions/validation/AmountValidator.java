package com.banking.transactions.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.math.BigDecimal;

public class AmountValidator implements ConstraintValidator<ValidAmount, BigDecimal> {

    @Override
    public void initialize(ValidAmount constraintAnnotation) {
        ConstraintValidator.super.initialize(constraintAnnotation);
    }

    @Override
    public boolean isValid(BigDecimal amount, ConstraintValidatorContext context) {
        if (amount == null) {
            return false;
        }

        // Check if amount is positive
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            if (context != null) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate("Amount must be a positive number")
                        .addConstraintViolation();
            }
            return false;
        }

        // Check decimal places (scale)
        if (amount.scale() > 2) {
            if (context != null) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate("Amount must have maximum 2 decimal places")
                        .addConstraintViolation();
            }
            return false;
        }

        return true;
    }
}
