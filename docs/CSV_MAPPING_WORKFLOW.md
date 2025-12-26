# CSV-Based User Mapping Workflow

## Overview

This is **THE PRACTICAL APPROACH** for real migrations. Instead of hardcoding mappings in code, you use a CSV file that's easy to create, review, and maintain.

---

## What You Need to Provide

### Required: CSV file with 2 columns

**Minimum:**
```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
ajones,alice.jones@company.com
admin,admin.tableau@company.com
```

**Recommended (with Notes):**
```csv
ServerUsername,CloudEmail,Notes
jsmith,john.smith@company.com,Sales Manager - needs full name
ajones,alice.jones@company.com,Marketing Director
admin,admin.tableau@company.com,Admin account - special handling
```

That's it! The SDK reads this CSV and handles everything else.

---

## The Complete Workflow

### Phase 1: Get Your User List

**Option A: Export from Tableau Server Admin UI**
1. Sign in to Tableau Server as admin
2. Navigate to **Users** page
3. Click **Export** or **Download CSV**
4. You get a file with all users

**Option B: Use SQL (if you have database access)**
```sql
SELECT
    name as ServerUsername,
    email as ServerEmail,
    site_role,
    last_login
FROM users
WHERE active = true
ORDER BY name;
```

**Option C: Use the SDK Helper** (Example 6 includes this)
```csharp
await CsvMappingHelper.ExportUserTemplateCsv(
    serverUrl: "https://tableau-server.company.com",
    siteContentUrl: "default",
    accessTokenName: "your-token",
    accessToken: "your-secret",
    outputCsvPath: "user_export.csv"
);
```

This creates a CSV with ServerUsername and pre-filled CloudEmail columns you can edit.

---

### Phase 2: Create Your Mapping CSV

**Step 1: Open the export in Excel/Google Sheets**

You'll see something like:
```
ServerUsername | CurrentEmail
---------------|------------------
jsmith         | jsmith@oldcompany.com
ajones         | ajones@oldcompany.com
bwilson        | bob.wilson@oldcompany.com
```

**Step 2: Add CloudEmail column**

Determine the Cloud email for each user:

```
ServerUsername | CurrentEmail              | CloudEmail (NEW)
---------------|---------------------------|---------------------------
jsmith         | jsmith@oldcompany.com     | john.smith@company.com
ajones         | ajones@oldcompany.com     | alice.jones@company.com
bwilson        | bob.wilson@oldcompany.com | bob.wilson@company.com
```

**Step 3: Handle special cases**

Add rows for service accounts, admins, etc.:

```
ServerUsername | CloudEmail                   | Notes
---------------|------------------------------|------------------
admin          | admin.tableau@company.com    | Admin account
svc_extracts   | svc.tableau@company.com      | Service account
guest          | guest.tableau@company.com    | Guest access
```

**Step 4: Save as CSV**

Save as **user_mappings.csv** (or any name you prefer).

Final format:
```csv
ServerUsername,CloudEmail,Notes
jsmith,john.smith@company.com,Sales Manager
ajones,alice.jones@company.com,Marketing Director
bwilson,bob.wilson@company.com,
admin,admin.tableau@company.com,Admin account
svc_extracts,svc.tableau@company.com,Service account
```

---

### Phase 3: Use CSV in Migration

**Your code looks like this:**

```csharp
var plan = migration.CreatePlanBuilder()
    .FromSourceTableauServer(...)
    .ToDestinationTableauCloud(...)

    // 👇 Just point to your CSV file
    .Mappings.Add<CsvUserMapping, IUser>(
        new CsvUserMapping("user_mappings.csv", "@company.com")
    )

    .Build();

await migration.ExecuteAsync(plan);
```

**That's it!** The SDK:
1. Reads your CSV
2. Creates a dictionary of mappings
3. Applies them to all users
4. Automatically updates subscription references

---

### Phase 4: Test & Validate

**Before full migration:**

1. **Create test CSV** with 5-10 users
2. **Migrate to test Cloud site** (not production!)
3. **Verify users created** correctly
4. **Test login** - users should login with their Cloud email
5. **Check subscriptions** - verify they use new emails

**Validation checklist:**
- ✅ All users in Cloud have correct emails
- ✅ Users can login with new email addresses
- ✅ Subscriptions exist in Cloud
- ✅ Subscription emails are being sent
- ✅ No errors in migration log

---

## CSV Format Details

### Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| **ServerUsername** | Username from Tableau Server | `jsmith` |
| **CloudEmail** | Email for Tableau Cloud (must include @) | `john.smith@company.com` |

### Optional Columns

You can add any columns you want for tracking:

| Column | Use Case | Example |
|--------|----------|---------|
| **Notes** | Your comments | `Sales Manager - needs follow up` |
| **Department** | User's department | `Sales`, `Marketing` |
| **Status** | Migration tracking | `Migrated`, `Pending`, `Skip` |
| **Manager** | User's manager | `john.doe@company.com` |
| **LastLogin** | Last Server login | `2025-01-15` |

The code only uses `ServerUsername` and `CloudEmail` - other columns are ignored.

---

## Excel/Google Sheets Tips

### Auto-fill CloudEmail column with formula:

**If username format is firstname.lastname:**
```excel
=A2&"@company.com"
```
This converts:
- `john.smith` → `john.smith@company.com`
- `alice.jones` → `alice.jones@company.com`

**If username is abbreviated (needs manual fix):**
1. Use formula as starting point
2. Highlight rows that need fixing
3. Manually update abbreviated ones

**Find abbreviated usernames:**
```excel
=IF(LEN(A2)<10, "CHECK", "OK")
```

This flags short usernames that might be abbreviated.

---

## Common CSV Scenarios

### Scenario 1: Most users follow pattern, few exceptions

**CSV has 100 users:**
- 90 follow pattern: `firstname.lastname` → add `@company.com`
- 10 are abbreviated: need manual lookup

**Approach:**
1. Use Excel formula for the 90: `=A2&"@company.com"`
2. Manually fix the 10 abbreviated ones
3. Save CSV

### Scenario 2: Mixed formats

**CSV has:**
- Some users already have `@oldcompany.com`
- Some have just usernames
- Some are service accounts

**CSV looks like:**
```csv
ServerUsername,CloudEmail,Notes
john.smith@oldcompany.com,john.smith@newcompany.com,Change domain
jsmith,john.smith@newcompany.com,Add full name
svc_account,svc.tableau@newcompany.com,Service account
```

### Scenario 3: Company acquisition/merger

**Two companies merging:**
- Company A: usernames like `jsmith`
- Company B: emails like `john.smith@companyb.com`
- New Cloud: everyone uses `@merged.com`

**CSV maps both:**
```csv
ServerUsername,CloudEmail,Notes
jsmith,john.smith@merged.com,From Company A
john.smith@companyb.com,john.smith@merged.com,From Company B
ajones,alice.jones@merged.com,From Company A
alice.j@companyb.com,alice.jones@merged.com,From Company B - different format
```

---

## Error Handling

### What if a user isn't in the CSV?

**Default behavior (in Example 6):**
```
Username not in CSV → append default domain
Example: "newuser" → "newuser@company.com"
```

You can change this to:
- Fail the migration (strict mode)
- Log a warning and skip
- Use different default domain

### What if CloudEmail is invalid?

**Tableau Cloud will reject:**
- Non-email formats (missing @)
- Invalid characters
- Too long (>254 chars)

**Migration will fail with error:**
```
Error: User 'jsmith' - invalid email format 'jsmithcompany.com'
```

**Fix:** Update CSV and re-run.

### What if duplicate CloudEmail?

**Two Server users → same Cloud email:**
```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
john.smith,john.smith@company.com  ← Duplicate!
```

**Cloud will reject:** Can't have duplicate emails.

**Fix:** Ensure each CloudEmail is unique.

---

## Testing Your CSV

### Quick Validation Script

Before running full migration, validate your CSV:

```csharp
var mappings = new CsvUserMapping("user_mappings.csv");

// Test a few known users
var testUsers = new[] { "jsmith", "ajones", "admin" };

foreach (var username in testUsers)
{
    var email = mappings.GetMappedEmail(username);
    Console.WriteLine($"{username} → {email}");
}

// Check for issues
// - All CloudEmail values contain @?
// - No duplicate CloudEmail?
// - All required users present?
```

---

## Real-World Example

### Before Migration

**Tableau Server (On-Prem):**
```
Users: 150 people
Formats:
  - 100 users: firstname.lastname (e.g., john.smith)
  - 40 users: abbreviated (e.g., jsmith)
  - 10 users: service accounts (e.g., svc_extracts)

Subscriptions: 75 subscriptions across these users
```

### Step 1: Export users

Export → `server_users.csv`

### Step 2: Create mapping CSV

Open in Excel, add CloudEmail column:
- Formula for standard: `=A2&"@company.com"`
- Manually fix 40 abbreviated
- Special emails for 10 service accounts

Save → `user_mappings.csv` (150 rows)

### Step 3: Review

Have team review the CSV:
- Sales manager reviews their team
- IT reviews service accounts
- HR confirms departures aren't included

### Step 4: Test

Migrate 10 users to test site:
```csv
ServerUsername,CloudEmail,Notes
jsmith,john.smith@company.com,Test user 1
ajones,alice.jones@company.com,Test user 2
...
```

Verify: ✅ Users created, ✅ Can login, ✅ Subscriptions work

### Step 5: Production

Use full 150-user CSV:
```csharp
var mapping = new CsvUserMapping("user_mappings.csv");
// Migration runs...
```

**Result:**
- ✅ 150 users migrated with correct emails
- ✅ 75 subscriptions automatically updated
- ✅ All references working in Cloud

---

## Advantages of CSV Approach

| Benefit | Why It Matters |
|---------|----------------|
| **Reviewable** | Open in Excel, easy to scan |
| **Collaborative** | Share with team for input |
| **Auditable** | Keep record of what was mapped |
| **Editable** | Change without touching code |
| **Reusable** | Use for future migrations |
| **Testable** | Test with subset easily |
| **Version Control** | Track changes in git |
| **No Code Changes** | Update CSV, not source code |

---

## Files You'll Create

```
your-migration-project/
├── user_mappings.csv          ← Your mapping file (main)
├── user_mappings_test.csv     ← Subset for testing
├── server_users_export.csv    ← Original export (backup)
├── user_mappings_v1.csv       ← Version history
├── user_mappings_v2.csv       ← Version history
└── validation_results.txt     ← Validation output
```

---

## Summary

**What you provide:**
```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
ajones,alice.jones@company.com
```

**What the SDK does:**
1. ✅ Reads CSV
2. ✅ Migrates users with mapped emails
3. ✅ Updates all subscription references automatically
4. ✅ Updates all content ownership
5. ✅ Updates all permissions

**You never touch subscriptions directly - they just work!**

---

## Quick Start Checklist

- [ ] Export users from Tableau Server
- [ ] Create user_mappings.csv with ServerUsername and CloudEmail columns
- [ ] Use Excel formula to pre-fill most emails
- [ ] Manually fix abbreviated/special usernames
- [ ] Add Notes column for tracking
- [ ] Test with 5-10 users first
- [ ] Verify subscriptions work in test
- [ ] Run full migration with complete CSV
- [ ] Keep CSV file for records

**See Example 6 (6_CSVBasedUserMapping.cs) for the complete working code.**
