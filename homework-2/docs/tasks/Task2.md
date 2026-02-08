## 📋 Project Overview
    Build a customer support ticket management system that imports tickets from multiple file formats, automatically categorizes issues, and assigns priorities.
### Task 2: Multi-Format Ticket Import API
    **Auto-Classification**
    Implement automatic ticket categorization and priority assignment.
#### Categories:
    - account_access - login, password, 2FA issues
    technical_issue - bugs, errors, crashes
    billing_question - payments, invoices, refunds
    feature_request - enhancements, suggestions
    bug_report - defects with reproduction steps
    other - uncategorizable
#### Priority Rules:
    Urgent: "can't access", "critical", "production down", "security"
    High: "important", "blocking", "asap"
    Medium: default
    Low: "minor", "cosmetic", "suggestion"
#### Endpoint:
    POST /tickets/:id/auto-classify
    Response includes: category, priority, confidence score (0-1), reasoning, keywords found

### Requirements:
    Auto-run on ticket creation (optional flag)
    Store classification confidence
    Allow manual override
    Log all decisions

### Constraints:
    No test are needed for this task
    No documentation is needed for this task
    Create only short document how-to-run md formated file
    Use as **Tech Stack:** Python Flask
    Use as a home folder: homework-2
    Use best practices for code organization
    Comment your code
    Create a high level plan first and save it in a file with md format
    Create merge request to homework-2-submission branch in this repository
