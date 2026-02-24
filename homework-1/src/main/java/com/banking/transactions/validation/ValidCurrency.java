package com.banking.transactions.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = CurrencyValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidCurrency {
    String message() default "Invalid currency code. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP, JPY)";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
