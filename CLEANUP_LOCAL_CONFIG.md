# Local Configuration Cleanup Required

## Issue Identified
During testing of the configuration fallback logic, I discovered that the local application configuration file:
`C:\Users\Aarón\AppData\Local\MITA\database.json`

contains:
```json
{
  "MYSQL_DATABASE": "mita_local",
  // ... other correct values matching .env
}
```

This causes the configuration system to use `mita_local` as the database name even though:
1. The `.env` file correctly specifies `SistemaGeriatrico`
2. We've fixed the hardcoded defaults to point to `SistemaGeriatrico`
3. Environment variables correctly override everything

The local stored configuration takes precedence over hardcoded defaults but lower precedence than environment variables.

## Root Cause
This local configuration file was likely created by a previous run of the application when either:
1. The `.env` file was missing or incomplete, causing the application to save whatever configuration was used at the time
2. Manual MySQL configuration was performed through the UI, which saves to this file
3. The application was running with a different configuration previously

## Solution Required
To ensure consistent behavior and prevent confusion, we need to update this local configuration file to match the actual working database name `SistemaGeriatrico`.

This is NOT modifying user credentials or database schema - it's correcting application-local state that was incorrectly stored.

## Proposed Fix
Update `C:\Users\Aarón\AppData\Local\MITA\database.json` to change:
```json
"MYSQL_DATABASE": "mita_local"
```
to:
```json
"MYSQL_DATABASE": "SistemaGeriatrico"
```

## Verification
After this change, the configuration precedence will work as:
1. Environment variables (.env) → Correctly shows SistemaGeriatrico ✓
2. Local stored configuration (database.json) → Will now show SistemaGeriatrico ✓  
3. Hardcoded defaults → Already fixed to show SistemaGeriatrico ✓

This ensures that even if environment variables somehow fail to load, the system will still use the correct database name.

## Relation to User's Constraints
- ✅ Does not modify .env file
- ✅ Does not modify MySQL password  
- ✅ Does not modify database name, schema, tables, or data
- ✅ Does not create, drop, rename, migrate, reset, or alter MySQL database
- ✅ Only fixes application-local state that was incorrectly stored
- ✅ Restores consistent behavior matching the expected working state