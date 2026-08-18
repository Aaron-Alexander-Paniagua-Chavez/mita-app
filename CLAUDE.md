# MITA — Project Instructions

## 1. Project Overview

MITA is a Python desktop application for geriatric support.

Main technologies:
- Python
- CustomTkinter / Tkinter
- MySQL 8.0
- MongoDB
- Git

The project is currently being developed and stabilized after work from multiple AI agents.

The main objective is to finish the existing implementation without destroying or unnecessarily rewriting working functionality.

---

# 2. CRITICAL RULES — READ BEFORE MODIFYING ANYTHING

## NEVER destroy existing work

Do NOT:
- run `git reset --hard`
- reset the project to an older commit
- rebase the project unless explicitly requested
- delete existing features just because they are incomplete
- perform massive rewrites
- replace working systems with new implementations without a clear reason

Before making significant changes:
1. Inspect the existing implementation.
2. Understand how the current architecture works.
3. Identify dependencies between modules.
4. Make the smallest safe change possible.

---

# 3. DATABASE SAFETY — HIGHEST PRIORITY

This is the most important rule in the project.

## MySQL

The existing MySQL database is:

    SistemaGeriatrico

The current local configuration is:

    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    MYSQL_DATABASE=SistemaGeriatrico
    MYSQL_USER=root

The password is stored ONLY in `.env`.

NEVER:
- delete the database
- drop tables
- erase existing data
- replace the database with a new database
- change the database name
- change the user's password
- hard-code the password
- require the user to manually configure MySQL during normal startup

Do NOT use destructive commands such as:

    DROP DATABASE
    DROP TABLE
    TRUNCATE TABLE

unless the user explicitly requests it.

Database initialization must be safe and idempotent.

Prefer:

    CREATE TABLE IF NOT EXISTS

and equivalent non-destructive operations.

If a schema change is necessary:
1. Inspect the current schema first.
2. Determine whether the table/column already exists.
3. Make an additive migration.
4. Preserve all existing data.

---

# 4. MySQL CONFIGURATION

MITA must automatically use the existing `.env`.

The `.env` file contains the local MySQL password.

Do NOT change:

    MYSQL_USER=root

to:

    MYSQL_USER=root@localhost

`localhost` belongs in `MYSQL_HOST`, not in `MYSQL_USER`.

The application should attempt to connect automatically using `.env`.

The user should NOT be forced to open "Configurar MySQL" when the correct `.env` configuration already exists.

If MySQL cannot connect:
- show a useful diagnostic
- do not silently change credentials
- do not overwrite `.env`
- do not create another database automatically unless explicitly intended by the existing architecture

---

# 5. MONGODB

MongoDB is intentionally part of MITA.

Current configuration:

    MONGO_URI=mongodb://localhost:27017
    MONGO_DATABASE=mita_analytics

MongoDB is OPTIONAL.

MITA must continue working if MongoDB is unavailable.

MongoDB should be used for optional analytics/telemetry functionality.

Do NOT remove MongoDB.

Do NOT make MongoDB a mandatory dependency for application startup.

Before modifying MongoDB code:
- inspect the existing collections
- inspect how the application writes documents
- inspect how the application reads documents
- preserve existing data

---

# 6. INTERNET / CONNECTIVITY DETECTION

The project contains `core/connectivity.py`.

This functionality is intentional and must be preserved.

MITA should detect whether:
- Internet is available
- Internet is unavailable / local-only

Connectivity detection must NOT be confused with MySQL configuration.

The application must not require manual MySQL configuration simply because Internet connectivity changes.

The desired behavior is:

Internet available:
    MITA works normally
    Optional online services may be available

Internet unavailable:
    MITA continues working locally
    Optional online services are disabled gracefully

---

# 7. OPTIONAL ONLINE SERVICES

Remote services such as Gemini or MQTT are OPTIONAL.

API keys and credentials must never be hard-coded.

Use environment variables.

If an API key is missing:
- MITA must still start
- unrelated features must continue working
- the application should fail gracefully only for the optional feature requiring the key

Never commit `.env`.

Never expose secrets in logs, error messages, commits, or source code.

---

# 8. EXISTING FEATURES

Preserve and stabilize existing functionality, including:

- authentication
- user sessions
- role-based views
- accessibility
- high contrast
- themes
- Inter typography
- activity tracking
- time tracking
- preferences
- personalization
- statistics
- connectivity detection
- MongoDB analytics/telemetry
- MySQL persistence
- visual exercise guides

Do not remove these features unless they are demonstrably broken and the user explicitly approves their removal.

---

# 9. CHAT / AI FEATURES

Inspect:

    services/chat_service.py

This functionality may be incomplete.

Determine whether it is:
- fully implemented
- partially implemented
- broken
- unused

If it can be safely completed, complete it.

If it is incomplete and causes instability, disable it gracefully rather than leaving broken code that crashes MITA.

AI functionality must remain optional.

Never hard-code an API key.

---

# 10. SECURITY

Never expose or commit:
- MySQL passwords
- API keys
- session secrets
- private credentials
- `.env`

Before committing, verify:

    git status

and make sure `.env` is not included.

`.env.example` may contain placeholders but NEVER real secrets.

---

# 11. ENCODING

Some existing files may contain encoding corruption such as:

    configuraciÃ³n
    aplicaciÃ³n
    contraseÃ±a

Do not blindly rewrite the entire project.

If fixing encoding:
1. Identify the affected file.
2. Preserve the original content.
3. Convert it carefully to UTF-8.
4. Verify that Spanish characters display correctly.

Do not mix unrelated encoding changes into functional changes unless necessary.

---

# 12. CODE STYLE

Prefer:
- small changes
- readable code
- existing architecture
- existing interfaces
- existing naming conventions

Avoid:
- unnecessary abstractions
- duplicate database managers
- duplicate connection logic
- massive refactors
- replacing working modules without reason

Before adding a new system, check whether an existing implementation already provides the required functionality.

---

# 13. TESTING IS REQUIRED

Do not claim something works unless it was actually tested.

At minimum test:

## Python

Run:

    python -m compileall .

There must be no syntax errors.

## MySQL

Verify:
- MySQL connection works
- `SistemaGeriatrico` is used
- existing tables remain intact
- no existing data was deleted
- application can initialize/use MySQL

## MongoDB

Verify:
- `mita_analytics` can be accessed
- existing collections can be accessed
- documents can be read/written where appropriate
- application does not crash if MongoDB is unavailable

## Application

Start MITA and verify:
- application opens
- no traceback occurs
- MySQL does not require unnecessary manual configuration
- login works
- role selection works
- major views open

## Connectivity

Test:
- Internet available
- Internet unavailable

MITA should continue working locally when Internet is unavailable.

---

# 14. DATABASE VERIFICATION BEFORE CHANGES

Before modifying database code, inspect the current database.

For MySQL, verify:

    SHOW DATABASES;
    USE SistemaGeriatrico;
    SHOW TABLES;

Do not modify or delete anything merely for testing.

For MongoDB:

    show dbs
    use mita_analytics
    show collections

Use read-only inspection whenever possible.

---

# 15. GIT WORKFLOW

Before making major changes:

    git status

After modifications:

    git diff --stat
    git diff

Review the changes.

Do not commit:
- `.env`
- passwords
- API keys
- virtual environments
- `__pycache__`
- temporary files

Do not create a commit until testing is complete.

If everything works, create ONE clear commit.

Example:

    git add .
    git commit -m "Finalize MITA integration and stabilize databases"

Do NOT push automatically unless explicitly requested by the user.

---

# 16. WHEN SOMETHING FAILS

Do not immediately revert the entire project.

Instead:

1. Identify the exact error.
2. Locate the responsible module.
3. Inspect recent changes.
4. Compare with the previous known-working implementation if necessary.
5. Fix only the affected functionality.
6. Retest.

If a previous implementation was working and the new implementation broke it, prefer restoring the smallest affected portion rather than reverting unrelated work.

---

# 17. FINAL REPORT

At the end of the task, report:

1. Files modified
2. Features completed
3. Bugs fixed
4. MySQL status
5. MongoDB status
6. Connectivity detection status
7. Authentication status
8. Tests actually performed
9. Known remaining problems
10. Git commit created, if any

Be honest.

If something could not be tested, explicitly say:

    NOT TESTED

Never claim successful functionality without verification.

---

# 18. CURRENT PRIORITY

Work in this order:

1. Preserve MySQL data
2. Keep existing MySQL configuration working automatically
3. Keep MongoDB optional and functional
4. Preserve Internet/connectivity detection
5. Stabilize the existing application
6. Finish incomplete features
7. Test the application
8. Review Git changes
9. Commit only after successful testing

The priority is STABILITY and DATA SAFETY over adding new features.