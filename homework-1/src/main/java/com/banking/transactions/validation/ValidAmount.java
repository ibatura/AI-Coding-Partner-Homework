package com.banking.transactions.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Documented
@Constraint(validatedBy = AmountValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidAmount {
    String message() default "Amount must be a positive number with maximum 2 decimal places";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
