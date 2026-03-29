package com.banking.transactions.validation;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

class AmountValidatorTest {

    private final AmountValidator validator = new AmountValidator();

    @Test
    void testValidAmount() {
        assertTrue(validator.isValid(new BigDecimal("100.00"), null));
        assertTrue(validator.isValid(new BigDecimal("0.01"), null));
        assertTrue(validator.isValid(new BigDecimal("999999.99"), null));
    }

    @Test
    void testValidAmountWithOneDecimal() {
        assertTrue(validator.isValid(new BigDecimal("100.5"), null));
    }

    @Test
    void testValidAmountWithNoDecimals() {
        assertTrue(validator.isValid(new BigDecimal("100"), null));
    }

    @Test
    void testNullAmount() {
        assertFalse(validator.isValid(null, null));
    }

    @Test
    void testZeroAmount() {
        assertFalse(validator.isValid(BigDecimal.ZERO, null));
    }

    @Test
    void testNegativeAmount() {
        assertFalse(validator.isValid(new BigDecimal("-100.00"), null));
    }

    @Test
    void testMoreThanTwoDecimals() {
        assertFalse(validator.isValid(new BigDecimal("100.123"), null));
        assertFalse(validator.isValid(new BigDecimal("0.001"), null));
    }
}
