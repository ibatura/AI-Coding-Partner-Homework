package com.banking.transactions.validation;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class AccountNumberValidatorTest {

    private final AccountNumberValidator validator = new AccountNumberValidator();

    @Test
    void testValidAccountNumbers() {
        assertTrue(validator.isValid("ACC-12345", null));
        assertTrue(validator.isValid("ACC-ABCDE", null));
        assertTrue(validator.isValid("ACC-A1B2C", null));
        assertTrue(validator.isValid("ACC-ab123", null));
    }

    @Test
    void testInvalidAccountNumbers() {
        // Null or blank
        assertFalse(validator.isValid(null, null));
        assertFalse(validator.isValid("", null));
        assertFalse(validator.isValid("   ", null));

        // Wrong format
        assertFalse(validator.isValid("ACC-1234", null)); // Too short
        assertFalse(validator.isValid("ACC-123456", null)); // Too long
        assertFalse(validator.isValid("ACC12345", null)); // Missing dash
        assertFalse(validator.isValid("AC-12345", null)); // Wrong prefix
        assertFalse(validator.isValid("ACCT-12345", null)); // Wrong prefix

        // Special characters
        assertFalse(validator.isValid("ACC-1234@", null));
        assertFalse(validator.isValid("ACC-123-5", null));
        assertFalse(validator.isValid("ACC-123 5", null));
    }
}
