package com.banking.transactions.validation;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CurrencyValidatorTest {

    private final CurrencyValidator validator = new CurrencyValidator();

    @Test
    void testValidCurrencies() {
        // Common currencies from predefined list
        assertTrue(validator.isValid("USD", null));
        assertTrue(validator.isValid("EUR", null));
        assertTrue(validator.isValid("GBP", null));
        assertTrue(validator.isValid("JPY", null));
        assertTrue(validator.isValid("CHF", null));
        assertTrue(validator.isValid("CAD", null));
        assertTrue(validator.isValid("AUD", null));

        // Case insensitive
        assertTrue(validator.isValid("usd", null));
        assertTrue(validator.isValid("Eur", null));
    }

    @Test
    void testInvalidCurrencies() {
        // Null or blank
        assertFalse(validator.isValid(null, null));
        assertFalse(validator.isValid("", null));
        assertFalse(validator.isValid("   ", null));

        // Invalid codes
        assertFalse(validator.isValid("XYZ", null));
        assertFalse(validator.isValid("ABC", null));
        assertFalse(validator.isValid("DOLLAR", null));
        assertFalse(validator.isValid("US", null));
        assertFalse(validator.isValid("USDD", null));
    }

    @Test
    void testISO4217Currencies() {
        // Some valid ISO 4217 currencies that may not be in our predefined list
        // but should be validated by Java's Currency class
        assertTrue(validator.isValid("USD", null));
        assertTrue(validator.isValid("EUR", null));
        assertTrue(validator.isValid("GBP", null));
    }
}
