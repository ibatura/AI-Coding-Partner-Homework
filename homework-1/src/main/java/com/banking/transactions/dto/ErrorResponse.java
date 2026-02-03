package com.banking.transactions.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class ErrorResponse {
    private String error;
    private List<ValidationError> details;

    public ErrorResponse(String error) {
        this.error = error;
        this.details = null;
    }

    @Data
    @AllArgsConstructor
    public static class ValidationError {
        private String field;
        private String message;
    }
}
