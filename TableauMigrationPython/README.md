# Tableau Migration SDK - Python Examples

Complete Python examples for migrating from Tableau Server to Tableau Cloud, with focus on **subscriptions** and **user/project mapping**.

---

## Why Python?

✅ **Simpler than C#** - No dependency injection, less boilerplate
✅ **Familiar syntax** - If you know Python, you're ready to go
✅ **Built-in CSV** - No extra libraries needed for CSV mappings
✅ **Easy to test** - Quick iteration and debugging
✅ **Same SDK power** - All the features of the C# SDK

---

## Quick Start

### 1. Install the SDK

```bash
pip install -r requirements.txt
```

Or directly:
```bash
pip install tableau-migration
```

### 2. Run an Example

```bash
# Start with the basic example
python examples/1_basic_migration_setup.py

# Then try CSV-based mapping (most practical)
python examples/5_csv_based_user_mapping.py

# Or run the complete example
python examples/6_complete_subscription_migration.py
```

### 3. Customize for Your Environment

Edit the examples to match your:
- Server URL and credentials
- Cloud URL and credentials
- Project mappings
- User email mappings

---

## Examples Overview

### Example 1: Basic Migration Setup
**File:** `1_basic_migration_setup.py`

**What it shows:**
- Minimum code to run a migration
- Source/destination configuration
- Execution and result checking

**Use this to:** Understand the basic structure

---

### Example 2: Project Mapping
**File:** `2_project_mapping.py`

**What it shows:**
- How to rename projects during migration
- Dictionary-based mapping rules
- Automatic workbook relocation

**Use this when:** You need to rename projects (e.g., "Sales" → "Cloud - Sales")

**Real scenario:**
```python
PROJECT_MAPPINGS = {
    "Campaign Analytics": "Marketing - Campaigns",
    "Sales Metrics": "Sales - Metrics"
}
```

---

### Example 3: User Mapping for Subscriptions
**File:** `3_user_mapping_for_subscriptions.py`

**What it shows:**
- Email domain mapping (bulk changes)
- Specific user mappings (individual overrides)
- Why this is critical for subscriptions

**Use this when:** Email domains change during migration

**Real scenario:**
```python
# Change domain for everyone
OLD_DOMAIN = "@oldcompany.com"
NEW_DOMAIN = "@newcompany.com"

# Plus specific overrides
USERNAME_MAPPINGS = {
    "john.smith@oldcompany.com": "j.smith@newcompany.com"
}
```

---

### Example 4: Username to Email Mapping ⭐ MOST COMMON
**File:** `4_username_to_email_mapping.py`

**What it shows:**
- Converting Server usernames to Cloud emails
- Lookup tables for abbreviated usernames
- Fallback to default domain append

**Use this when:** Server uses simple usernames, Cloud needs emails

**Real scenario:**
```python
USERNAME_MAPPINGS = {
    "jsmith": "john.smith@company.com",      # Abbreviated
    "ajones": "alice.jones@company.com",     # Abbreviated
    "admin": "admin.tableau@company.com"     # Special account
}
```

This is **THE most common Cloud migration scenario**!

---

### Example 5: CSV-Based User Mapping ⭐ RECOMMENDED
**File:** `5_csv_based_user_mapping.py`

**What it shows:**
- Load mappings from CSV file (production approach)
- No hardcoding - edit CSV instead
- Team-friendly workflow

**Use this when:** You have 95%+ of your mappings in CSV format

**Your workflow:**
1. Export users from Server
2. Create CSV: `ServerUsername,CloudEmail`
3. Edit in Excel/Google Sheets
4. Save as `user_mappings.csv`
5. Run migration - SDK handles everything!

**CSV Format:**
```csv
ServerUsername,CloudEmail,Notes
jsmith,john.smith@company.com,Sales Manager
ajones,alice.jones@company.com,Marketing Director
admin,admin.tableau@company.com,Admin account
```

**Why this is best:**
- ✅ Easy to review in Excel
- ✅ No code changes for mapping updates
- ✅ Team can collaborate on CSV
- ✅ Reusable for future migrations
- ✅ Auditable record

---

### Example 6: Complete Subscription Migration ⭐ PRODUCTION
**File:** `6_complete_subscription_migration.py`

**What it shows:**
- Everything together: projects + users + subscriptions
- CSV-based user mapping
- Subscription filtering (exclude test subscriptions)
- Production-ready structure

**Use this as:** Your template for real migrations

**What it does:**
```
✅ Renames projects (Marketing → Cloud - Marketing)
✅ Maps users (jsmith → john.smith@company.com)
✅ Migrates subscriptions with updated references
✅ Filters out test subscriptions
✅ Reports detailed results
```

---

## How Subscriptions Work

### The Key Insight:

**You only define USER and PROJECT mappings.**
**The SDK automatically updates subscription references!**

### Example Flow:

```
SERVER:
User: jsmith
Project: Marketing
Workbook: "Sales Dashboard" (in Marketing project)
Subscription: jsmith → "Sales Dashboard"

YOUR MAPPINGS:
User: jsmith → john.smith@company.com
Project: Marketing → Cloud - Marketing

CLOUD (AUTOMATIC):
User: john.smith@company.com
Project: Cloud - Marketing
Workbook: "Sales Dashboard" (in Cloud - Marketing project)
Subscription: john.smith@company.com → "Sales Dashboard" ← UPDATED!
```

**You never touch subscriptions - SDK handles them!**

---

## CSV Workflow (Recommended)

### Step 1: Export Users

Get your user list from Tableau Server (Admin UI or SQL)

### Step 2: Create CSV

```csv
ServerUsername,CloudEmail,Notes
jsmith,john.smith@company.com,Needs full name
ajones,alice.jones@company.com,Needs full name
bob.wilson,bob.wilson@company.com,Already correct
admin,admin.tableau@company.com,Special account
```

### Step 3: Load in Code

```python
from examples.csv_based_user_mapping import CsvUserMapping

csv_mapping = CsvUserMapping("user_mappings.csv", "@company.com")
plan_builder.mappings.add(csv_mapping)
```

### Step 4: Run Migration

```bash
python examples/5_csv_based_user_mapping.py
```

**Done!** Subscriptions automatically use the new emails.

---

## Python vs C# Comparison

| Feature | Python | C# |
|---------|--------|-----|
| **Setup** | `pip install tableau-migration` | Nuget package + DI setup |
| **Code Length** | Shorter, cleaner | More boilerplate |
| **Mapping** | Simple class with `map()` method | Interface + DI registration |
| **CSV Handling** | Built-in `csv` module | Requires CsvHelper library |
| **Learning Curve** | Easier for beginners | Steeper for non-.NET devs |
| **Async** | Native `async/await` | Same `async/await` |
| **IDE Support** | Any Python IDE | VS/VS Code recommended |

**Both have the same SDK features and capabilities!**

---

## Common Scenarios

### Scenario 1: Simple domain append

```python
# Server: john.smith
# Cloud:  john.smith@company.com

class SimpleMapping:
    def map(self, ctx):
        username = ctx.content_item.name
        if "@" not in username:
            email = f"{username}@company.com"
            return ctx.map_to(ctx.content_item.location.with_username(email))
        return ctx
```

### Scenario 2: Abbreviated usernames (CSV)

```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
ajones,alice.jones@company.com
```

Use Example 5!

### Scenario 3: Project aggregation

```python
# Multiple sites → Single Cloud site with prefixes
PROJECT_MAPPINGS = {
    "Marketing": "Cloud - Marketing",
    "Sales": "Cloud - Sales",
    "Finance": "Cloud - Finance"
}
```

Use Example 2!

---

## Testing Your Migration

### Before Production:

1. **Create test CSV** with 5-10 users
2. **Migrate to test Cloud site** (not production!)
3. **Verify:**
   - Users created with correct emails
   - Projects renamed correctly
   - Workbooks in right projects
   - Subscriptions exist and work
4. **Test subscription emails** - do they arrive?

### Validation Checklist:

- [ ] All users can login with Cloud email
- [ ] Projects have correct names
- [ ] Workbooks in correct projects
- [ ] Subscriptions exist in Cloud
- [ ] Subscription emails are sent
- [ ] No errors in migration log

---

## Installation Details

### Requirements:

- Python 3.8 or higher
- pip (Python package manager)

### Install:

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install SDK directly
pip install tableau-migration
```

### Verify Installation:

```bash
python -c "import tableau_migration; print('SDK installed successfully!')"
```

---

## Troubleshooting

### Issue: "tableau_migration module not found"

**Solution:**
```bash
pip install tableau-migration
```

### Issue: "Invalid email format"

**Cause:** Cloud requires emails (with @)

**Solution:** Check your mapping - all Cloud emails must contain @

### Issue: "User not found in destination"

**Cause:** Subscription references a user that wasn't migrated

**Solution:** Ensure all users are in your CSV or default mapping

### Issue: Subscriptions not working

**Cause:** User mapping might be incorrect

**Solution:**
1. Check migration logs for user mappings
2. Verify Cloud users have correct emails
3. Test one subscription manually

---

## Next Steps

1. **Read:** `../SUBSCRIPTIONS_AND_MAPPING.md` for concepts
2. **Read:** `../CSV_MAPPING_WORKFLOW.md` for CSV workflow
3. **Try:** Example 1 (basic setup)
4. **Try:** Example 5 (CSV mapping)
5. **Customize:** Example 6 for your environment
6. **Test:** With small subset first
7. **Production:** Full migration

---

## Key Takeaways

1. **Subscriptions migrate automatically** when you map users
2. **CSV approach is best** for production (95% use case)
3. **Python is simpler** than C# for most people
4. **Test first** before production migration
5. **SDK handles complexity** - you just configure rules

---

## Additional Resources

- **Conceptual Docs:** `../SUBSCRIPTIONS_AND_MAPPING.md`
- **User Mapping Patterns:** `../USER_MAPPING_PATTERNS.md`
- **CSV Workflow:** `../CSV_MAPPING_WORKFLOW.md`
- **Official SDK Docs:** https://help.tableau.com/current/api/migration_sdk/en-us/
- **Python API Reference:** https://tableau.github.io/migration-sdk/api-python/

---

## Summary

**What you provide:**
- CSV file with user mappings OR
- Dictionary with project/user rules

**What SDK does:**
- ✅ Migrates users with correct emails
- ✅ Migrates projects with new names
- ✅ Migrates workbooks to new locations
- ✅ Migrates subscriptions with updated references
- ✅ Adjusts schedules for Cloud
- ✅ Handles errors gracefully

**You define the rules, SDK does the work!**
