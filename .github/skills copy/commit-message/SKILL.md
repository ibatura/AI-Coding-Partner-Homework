---
name: Generate commit message
description: Use this when the user asks for a commit message or to summarize staged changes
---

Analyze the currently staged changes (`git diff --cached`) and produce a commit message using the Conventional Commits format:

```
<type>(<scope>): <short summary>

<body>
```

Rules:
1. Run `git diff --cached` to see what is staged.
2. Choose one **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`.
3. Set **scope** to the main area affected (e.g. a folder or module name). Omit parentheses if scope is unclear.
4. Write a **short summary** (≤ 72 chars, imperative mood, no period).
5. Add a **body** only when the diff is non-trivial — briefly explain *what* and *why*, wrapped at 72 chars.
6. Output ONLY the commit message text, nothing else.
