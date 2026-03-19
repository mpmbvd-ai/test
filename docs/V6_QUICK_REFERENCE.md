# Tableau Migration SDK v6.0 - Quick Reference

## 🚀 Installation

### C#
```xml
<PackageReference Include="Tableau.Migration" Version="6.0.*" />
```

### Python
```bash
pip install tableau-migration>=6.0.0
```

---

## 📦 Manifest API (The Key Change)

### C# v6.0 API

```csharp
// Get migration result
var result = await migration.ExecuteAsync(plan, CancellationToken.None);

// Access manifest
var manifest = result.Manifest;

// Query entries by type - USE THIS v6.0 PATTERN ✅
var users = manifest.Entries.ForContentType<IUser>();
var groups = manifest.Entries.ForContentType<IGroup>();
var projects = manifest.Entries.ForContentType<IProject>();
var dataSources = manifest.Entries.ForContentType<IDataSource>();
var workbooks = manifest.Entries.ForContentType<IWorkbook>();
var subscriptions = manifest.Entries.ForContentType<ISubscription>();

// Count entries
Console.WriteLine($"Users: {manifest.Entries.ForContentType<IUser>().Count()}");

// Check migration status
if (result.Status == MigrationCompletionStatus.Completed)
{
    // Success!
}

// Get errors
foreach (var error in result.Errors)
{
    Console.WriteLine(error.Message);
}
```

### Python v6.0 API

```python
# Get migration result
result = await plan.execute_async()

# Access manifest
manifest = result.manifest

# Query entries by type - USE THIS v6.0 PATTERN ✅
users = manifest.entries.get_by_type('User')
groups = manifest.entries.get_by_type('Group')
projects = manifest.entries.get_by_type('Project')
data_sources = manifest.entries.get_by_type('DataSource')
workbooks = manifest.entries.get_by_type('Workbook')
subscriptions = manifest.entries.get_by_type('Subscription')

# Count entries
print(f"Users: {len(manifest.entries.get_by_type('User'))}")

# Check migration status
if result.status == MigrationCompletionStatus.COMPLETED:
    # Success!
    pass

# Get errors
for error in result.errors:
    print(error.message)
```

---

## ❌ What NOT to Use (v5.x Deprecated Patterns)

### C# - DON'T USE THESE:
```csharp
// ❌ DEPRECATED v5.x patterns
manifest.GetEntries<IUser>()           // Old method
manifest.Entries.OfType<IUser>()       // Old method
manifest.QueryEntries<IUser>()         // Never existed

// ✅ USE v6.0 INSTEAD
manifest.Entries.ForContentType<IUser>()
```

### Python - DON'T USE THESE:
```python
# ❌ DEPRECATED v5.x patterns
manifest.get_entries('User')           # Old method
manifest.entries.by_type('User')       # Old method
manifest.entries.get_by_type('user')   # Wrong case

# ✅ USE v6.0 INSTEAD
manifest.entries.get_by_type('User')   # PascalCase!
```

---

## 📋 Content Types Reference

| Content Type | C# Type | Python String | Description |
|--------------|---------|---------------|-------------|
| Users | `IUser` | `'User'` | User accounts |
| Groups | `IGroup` | `'Group'` | User groups |
| Projects | `IProject` | `'Project'` | Project folders |
| Data Sources | `IDataSource` | `'DataSource'` | Published data sources |
| Workbooks | `IWorkbook` | `'Workbook'` | Workbooks with views |
| Subscriptions | `ISubscription` | `'Subscription'` | Email subscriptions |

---

## 🔄 Complete Migration Pattern (C#)

```csharp
using Tableau.Migration;
using Tableau.Migration.Content;
using Tableau.Migration.Engine.Hooks.Mappings;

public async Task MigrateAsync()
{
    // 1. Setup host
    var host = Host.CreateDefaultBuilder()
        .ConfigureServices((ctx, services) =>
        {
            services.AddTableauMigration();
        })
        .Build();

    // 2. Get migration service
    var migration = host.Services.GetRequiredService<IMigration>();

    // 3. Build plan
    var plan = migration.CreatePlanBuilder()
        .FromSourceTableauServer(
            new Uri("https://server.company.com"),
            "site-name",
            "token-name",
            "token-secret"
        )
        .ToDestinationTableauCloud(
            new Uri("https://10ax.online.tableau.com"),
            "cloud-site",
            "cloud-token-name",
            "cloud-token-secret"
        )
        .Mappings.Add<MyUserMapping, IUser>()
        .Build();

    // 4. Execute
    var result = await migration.ExecuteAsync(plan, CancellationToken.None);

    // 5. Check results (v6.0 API)
    if (result.Status == MigrationCompletionStatus.Completed)
    {
        var manifest = result.Manifest;

        Console.WriteLine("✅ Migration completed!");
        Console.WriteLine($"Users:         {manifest.Entries.ForContentType<IUser>().Count()}");
        Console.WriteLine($"Projects:      {manifest.Entries.ForContentType<IProject>().Count()}");
        Console.WriteLine($"Workbooks:     {manifest.Entries.ForContentType<IWorkbook>().Count()}");
        Console.WriteLine($"Subscriptions: {manifest.Entries.ForContentType<ISubscription>().Count()}");
    }
    else
    {
        Console.WriteLine($"❌ Failed: {result.Status}");
        foreach (var error in result.Errors)
        {
            Console.WriteLine($"  {error.Message}");
        }
    }
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Count All Migrated Content

```csharp
var manifest = result.Manifest;

var summary = new
{
    Users = manifest.Entries.ForContentType<IUser>().Count(),
    Groups = manifest.Entries.ForContentType<IGroup>().Count(),
    Projects = manifest.Entries.ForContentType<IProject>().Count(),
    DataSources = manifest.Entries.ForContentType<IDataSource>().Count(),
    Workbooks = manifest.Entries.ForContentType<IWorkbook>().Count(),
    Subscriptions = manifest.Entries.ForContentType<ISubscription>().Count()
};

Console.WriteLine($"Migrated: {summary.Users} users, {summary.Workbooks} workbooks");
```

### Use Case 2: Find Failed Migrations

```csharp
var failedUsers = manifest.Entries
    .ForContentType<IUser>()
    .Where(e => e.Status == MigrationManifestEntryStatus.Error);

foreach (var failed in failedUsers)
{
    Console.WriteLine($"❌ {failed.Source.Name}: {string.Join(", ", failed.Errors.Select(e => e.Message))}");
}
```

### Use Case 3: Export Mappings to CSV

```csharp
var users = manifest.Entries.ForContentType<IUser>();

using var writer = new StreamWriter("user_mappings.csv");
writer.WriteLine("SourceUsername,DestinationUsername,Status");

foreach (var user in users)
{
    writer.WriteLine($"{user.Source.Name},{user.Destination?.Name ?? "N/A"},{user.Status}");
}
```

### Use Case 4: Verify Subscriptions

```csharp
var subscriptions = manifest.Entries.ForContentType<ISubscription>();

Console.WriteLine($"📧 Total subscriptions: {subscriptions.Count()}");

var successful = subscriptions.Count(s => s.Status == MigrationManifestEntryStatus.Migrated);
var failed = subscriptions.Count(s => s.Status == MigrationManifestEntryStatus.Error);

Console.WriteLine($"  ✅ Successful: {successful}");
Console.WriteLine($"  ❌ Failed: {failed}");
```

---

## 🐛 Troubleshooting

### "ForContentType not found" Error

**Problem:**
```
Error CS1061: does not contain a definition for 'ForContentType'
```

**Solution:**
```bash
# Update to v6.0
dotnet add package Tableau.Migration --version 6.0.*
dotnet restore
dotnet build
```

### Empty Manifest

**Problem:**
```csharp
manifest.Entries.ForContentType<IUser>().Count() == 0
```

**Check:**
1. Migration completed? `result.Status == MigrationCompletionStatus.Completed`
2. Any errors? `result.Errors`
3. Filters excluding content?

### Type Name Case Issues (Python)

**Problem:**
```python
manifest.entries.get_by_type('user')  # Returns nothing
```

**Solution:**
```python
manifest.entries.get_by_type('User')  # Use PascalCase!
```

---

## 📚 Learn More

- **Full Guide**: [V6_MIGRATION_GUIDE.md](./V6_MIGRATION_GUIDE.md)
- **Examples**: `archive/csharp-examples/Examples/`
- **Patterns**: [USER_MAPPING_PATTERNS.md](./USER_MAPPING_PATTERNS.md)

---

## ✅ v6.0 Checklist

- [ ] Updated package to v6.0
- [ ] Changed `manifest.GetEntries<T>()` → `manifest.Entries.ForContentType<T>()`
- [ ] Using PascalCase type names in Python
- [ ] Tested migration end-to-end
- [ ] Updated documentation

**You're ready for v6.0!** 🚀
