# User Mapping Patterns for Cloud Migration

## The Core Problem

**Tableau Server** → Uses simple usernames (any string)
**Tableau Cloud** → Requires email addresses (must contain @)

**Impact on Subscriptions:**
Subscriptions are tied to users. If user mapping is wrong, subscriptions break!

---

## Common Migration Scenarios

### Scenario 1: Username = Email Format (Easiest)
**Server usernames already look like emails**

**Example:**
```
Server: john.smith@company.com
Cloud:  john.smith@company.com
```

**Mapping:** None needed! ✅

**Code:**
```csharp
// No mapping needed - usernames are already emails
// SDK will use them as-is
```

---

### Scenario 2: Simple Username + Domain (Most Common)
**Server uses firstname.lastname, need to add domain**

**Example:**
```
Server: john.smith
Cloud:  john.smith@company.com
```

**Mapping:** Append domain

**Code:**
```csharp
public class AppendDomainMapping : ContentMappingBase<IUser>
{
    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx, CancellationToken cancel)
    {
        var username = ctx.ContentItem.Name;

        if (!username.Contains("@"))
        {
            var email = $"{username}@company.com";
            return ctx.MapTo(ctx.ContentItem.Location.WithUsername(email));
        }

        return ctx;
    }
}
```

---

### Scenario 3: Abbreviated Usernames (Needs Lookup)
**Server uses short codes, need full email**

**Example:**
```
Server: jsmith
Cloud:  john.smith@company.com

Server: ajones
Cloud:  alice.jones@company.com
```

**Mapping:** Dictionary lookup + default rule

**Code:**
```csharp
public class LookupMapping : ContentMappingBase<IUser>
{
    private static readonly Dictionary<string, string> Map = new()
    {
        { "jsmith", "john.smith@company.com" },
        { "ajones", "alice.jones@company.com" }
    };

    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx, CancellationToken cancel)
    {
        var username = ctx.ContentItem.Name;

        if (Map.TryGetValue(username, out var email))
        {
            return ctx.MapTo(ctx.ContentItem.Location.WithUsername(email));
        }

        // Default: append domain
        return ctx.MapTo(ctx.ContentItem.Location.WithUsername($"{username}@company.com"));
    }
}
```

---

### Scenario 4: Mixed Formats (Complex)
**Some users have emails, others don't**

**Example:**
```
Server: john.smith@company.com  (already email)
Server: bjones                   (needs domain)
Server: admin                    (special case)
```

**Mapping:** Check format, apply appropriate rule

**Code:**
```csharp
public class MixedFormatMapping : ContentMappingBase<IUser>
{
    private static readonly Dictionary<string, string> SpecialCases = new()
    {
        { "admin", "admin.tableau@company.com" },
        { "service", "svc.tableau@company.com" }
    };

    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx, CancellationToken cancel)
    {
        var username = ctx.ContentItem.Name;

        // Already an email? Use as-is
        if (username.Contains("@"))
        {
            return ctx;
        }

        // Special case?
        if (SpecialCases.TryGetValue(username, out var specialEmail))
        {
            return ctx.MapTo(ctx.ContentItem.Location.WithUsername(specialEmail));
        }

        // Default: append domain
        var email = $"{username}@company.com";
        return ctx.MapTo(ctx.ContentItem.Location.WithUsername(email));
    }
}
```

---

### Scenario 5: Domain Change (Server has emails, but wrong domain)
**Server uses old company domain, Cloud uses new domain**

**Example:**
```
Server: john.smith@oldcompany.com
Cloud:  john.smith@newcompany.com
```

**Mapping:** Replace domain

**Code:**
```csharp
public class DomainChangeMapping : ContentMappingBase<IUser>
{
    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx, CancellationToken cancel)
    {
        var email = ctx.ContentItem.Email;

        if (email.EndsWith("@oldcompany.com"))
        {
            var newEmail = email.Replace("@oldcompany.com", "@newcompany.com");
            return ctx.MapTo(ctx.ContentItem.Location.WithUsername(newEmail));
        }

        return ctx;
    }
}
```

---

## How Subscriptions Use These Mappings

### The Flow:

```
1. SERVER SUBSCRIPTION:
   User: "jsmith"
   Workbook: "Sales Dashboard"

2. MIGRATION READS SUBSCRIPTION:
   SDK: "Found subscription for user 'jsmith'"

3. SDK APPLIES USER MAPPING:
   Mapping: "jsmith" → "john.smith@company.com"

4. SDK CREATES USER IN CLOUD:
   Cloud User: "john.smith@company.com"

5. SDK CREATES SUBSCRIPTION IN CLOUD:
   User: "john.smith@company.com"  ← Automatically mapped!
   Workbook: "Sales Dashboard"
```

**You never manually update subscriptions - SDK does it automatically using your mapping rules!**

---

## Building Your Mapping Strategy

### Step 1: Audit Your Users

Export user list from Server:
```sql
SELECT
    name as ServerUsername,
    email as ServerEmail
FROM users;
```

### Step 2: Identify Patterns

Categorize your users:
- ✅ Already emails: No mapping needed
- 📧 Simple usernames: Append domain
- 🔍 Abbreviated: Need lookup table
- ⚙️ Special accounts: Individual mapping

### Step 3: Build Mapping Dictionary

Create a spreadsheet:
```
Server Username    | Cloud Email              | Method
-----------------------------------------------------------
john.smith        | john.smith@company.com   | Append domain
jsmith            | john.smith@company.com   | Lookup
admin             | admin.tableau@company.com| Special case
```

### Step 4: Implement in Code

```csharp
// Start with lookup table for exceptions
var specialMappings = new Dictionary<string, string>
{
    { "jsmith", "john.smith@company.com" },
    { "admin", "admin.tableau@company.com" }
};

// Then fall back to append domain for standard users
// (See Scenario 3 code above)
```

### Step 5: Test

1. Migrate a small test site first
2. Verify users can login (using their email)
3. Check subscriptions are working
4. Validate email delivery

---

## Common Issues & Solutions

### Issue 1: Users can't login after migration
**Problem:** User tries to login with "jsmith" but Cloud expects "john.smith@company.com"

**Solution:** Users must login with their email address on Cloud, not username

**Communication:**
"After migration, login to Tableau Cloud using your email: john.smith@company.com"

---

### Issue 2: Subscriptions not received
**Problem:** Subscription exists but emails don't arrive

**Causes:**
1. Email address is incorrect in Cloud
2. User mapping was wrong
3. Cloud email settings not configured

**Debug:**
```csharp
// Check what email was actually used
var manifest = result.Manifest;
var users = manifest.Entries.ForContentType<IUser>();

foreach (var user in users)
{
    Console.WriteLine($"Migrated: {user.Source.Location} → {user.Destination.Location}");
}
```

---

### Issue 3: Some subscriptions work, others don't
**Problem:** Inconsistent subscription behavior

**Cause:** Mixed username formats on Server

**Solution:** Use comprehensive mapping (Scenario 4) that handles all formats

---

## Quick Reference: Which Mapping Do I Need?

| Your Server Usernames Look Like | Mapping Needed | See Example |
|----------------------------------|----------------|-------------|
| john.smith@company.com          | None           | No code needed |
| john.smith                      | Append domain  | Scenario 2 |
| jsmith                          | Lookup table   | Scenario 3 |
| Mixed formats                   | Complex mapping| Scenario 4 |
| john@oldcompany.com            | Domain change  | Scenario 5 |

---

## Testing Your Mapping

### Test Script:

```csharp
// 1. List all source users
var sourceUsers = new[] { "jsmith", "ajones", "admin", "bob.wilson" };

// 2. Apply your mapping logic
var mapper = new YourMappingClass();

// 3. See results
foreach (var username in sourceUsers)
{
    var email = ApplyMapping(username); // Your logic here
    Console.WriteLine($"{username} → {email}");
}

// Expected output:
// jsmith → john.smith@company.com
// ajones → alice.jones@company.com
// admin → admin.tableau@company.com
// bob.wilson → bob.wilson@company.com
```

---

## Summary

1. **Identify your pattern** - How are Server usernames formatted?
2. **Choose mapping approach** - Append domain, lookup, or mixed
3. **Implement mapping class** - Use examples above
4. **Test with small subset** - Verify before full migration
5. **SDK handles subscriptions** - They automatically use mapped emails

**The key insight:** You only define USER mapping rules. The SDK automatically updates all subscription references to use the mapped emails!
