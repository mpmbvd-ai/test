# Tableau Migration SDK v6.0 - Migration Guide

## 🎯 Overview

This guide covers the key differences between Tableau Migration SDK v5.x and v6.0, and how to update your migration code to use the new v6.0 API.

## 📋 Table of Contents

1. [What's New in v6.0](#whats-new-in-v60)
2. [Manifest API Changes](#manifest-api-changes)
3. [Breaking Changes](#breaking-changes)
4. [Migration Steps](#migration-steps)
5. [Code Examples](#code-examples)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 What's New in v6.0

### Key Improvements

- **Improved Manifest API**: Type-safe querying of migration results
- **Better Error Reporting**: Enhanced error tracking and diagnostics
- **Streamlined Plan Builder**: More intuitive API for building migration plans
- **Enhanced Type Safety**: Generic methods for content type queries
- **Improved Performance**: Optimized manifest processing

### Version Compatibility

- **Minimum .NET Version**: .NET 8.0
- **Supported Platforms**: Windows, Linux, macOS
- **Tableau Server**: 2021.1 and later
- **Tableau Cloud**: All versions

---

## 📦 Manifest API Changes

### The Big Change: Manifest Entry Queries

The most significant change in v6.0 is how you query manifest entries.

### C# API Changes

#### ❌ v5.x Pattern (DEPRECATED)
```csharp
// v5.x used different methods
var users = manifest.GetEntries<IUser>();
// OR
var users = manifest.Entries.OfType<IUser>();
```

#### ✅ v6.0 Pattern (CURRENT)
```csharp
// v6.0 uses ForContentType<T>() method
var users = manifest.Entries.ForContentType<IUser>();
var groups = manifest.Entries.ForContentType<IGroup>();
var projects = manifest.Entries.ForContentType<IProject>();
var dataSources = manifest.Entries.ForContentType<IDataSource>();
var workbooks = manifest.Entries.ForContentType<IWorkbook>();
var subscriptions = manifest.Entries.ForContentType<ISubscription>();
```

### Python API Changes

#### ❌ v5.x Pattern (DEPRECATED)
```python
# v5.x used different methods
users = manifest.get_entries('User')
# OR
users = manifest.entries.by_type('User')
```

#### ✅ v6.0 Pattern (CURRENT)
```python
# v6.0 uses get_by_type() method
users = manifest.entries.get_by_type('User')
groups = manifest.entries.get_by_type('Group')
projects = manifest.entries.get_by_type('Project')
data_sources = manifest.entries.get_by_type('DataSource')
workbooks = manifest.entries.get_by_type('Workbook')
subscriptions = manifest.entries.get_by_type('Subscription')
```

### Complete v6.0 Manifest Example (C#)

```csharp
// Execute migration
var result = await migration.ExecuteAsync(plan, CancellationToken.None);

// Check status
if (result.Status == MigrationCompletionStatus.Completed)
{
    // Access manifest
    var manifest = result.Manifest;

    // Query entries using v6.0 API
    var userCount = manifest.Entries.ForContentType<IUser>().Count();
    var groupCount = manifest.Entries.ForContentType<IGroup>().Count();
    var projectCount = manifest.Entries.ForContentType<IProject>().Count();
    var dataSourceCount = manifest.Entries.ForContentType<IDataSource>().Count();
    var workbookCount = manifest.Entries.ForContentType<IWorkbook>().Count();
    var subscriptionCount = manifest.Entries.ForContentType<ISubscription>().Count();

    // Display results
    Console.WriteLine($"Users:         {userCount}");
    Console.WriteLine($"Groups:        {groupCount}");
    Console.WriteLine($"Projects:      {projectCount}");
    Console.WriteLine($"Data Sources:  {dataSourceCount}");
    Console.WriteLine($"Workbooks:     {workbookCount}");
    Console.WriteLine($"Subscriptions: {subscriptionCount}");

    // Access individual entries
    foreach (var userEntry in manifest.Entries.ForContentType<IUser>())
    {
        Console.WriteLine($"Migrated: {userEntry.Source.Name} → {userEntry.Destination?.Name}");
    }
}
else
{
    // Handle errors
    Console.WriteLine($"Migration failed: {result.Status}");
    foreach (var error in result.Errors)
    {
        Console.WriteLine($"Error: {error.Message}");
    }
}
```

### Complete v6.0 Manifest Example (Python)

```python
# Execute migration
result = await plan.execute_async()

# Check status
if result.status == MigrationCompletionStatus.COMPLETED:
    # Access manifest
    manifest = result.manifest

    # Query entries using v6.0 API
    user_count = len(manifest.entries.get_by_type('User'))
    group_count = len(manifest.entries.get_by_type('Group'))
    project_count = len(manifest.entries.get_by_type('Project'))
    data_source_count = len(manifest.entries.get_by_type('DataSource'))
    workbook_count = len(manifest.entries.get_by_type('Workbook'))
    subscription_count = len(manifest.entries.get_by_type('Subscription'))

    # Display results
    print(f"Users:         {user_count}")
    print(f"Groups:        {group_count}")
    print(f"Projects:      {project_count}")
    print(f"Data Sources:  {data_source_count}")
    print(f"Workbooks:     {workbook_count}")
    print(f"Subscriptions: {subscription_count}")

    # Access individual entries
    for user_entry in manifest.entries.get_by_type('User'):
        print(f"Migrated: {user_entry.source.name} → {user_entry.destination.name}")
else:
    # Handle errors
    print(f"Migration failed: {result.status}")
    for error in result.errors:
        print(f"Error: {error.message}")
```

---

## 💥 Breaking Changes

### 1. Manifest Entry Query Methods

**What Changed:**
- v5.x: `manifest.GetEntries<T>()` or `manifest.Entries.OfType<T>()`
- v6.0: `manifest.Entries.ForContentType<T>()`

**Action Required:**
Replace all manifest query methods with `ForContentType<T>()` in C# or `get_by_type()` in Python.

### 2. Type Names in Python

**What Changed:**
Content type names are now standardized.

**v5.x Python:**
```python
manifest.entries.by_type('user')  # lowercase
```

**v6.0 Python:**
```python
manifest.entries.get_by_type('User')  # PascalCase
```

**Action Required:**
Use PascalCase type names: `'User'`, `'Group'`, `'Project'`, `'DataSource'`, `'Workbook'`, `'Subscription'`

### 3. Result Property Access

**No change required** - the following still works in v6.0:
```csharp
var manifest = result.Manifest;  // Still correct
var status = result.Status;      // Still correct
var errors = result.Errors;      // Still correct
```

---

## 🔄 Migration Steps

### Step 1: Update Package Reference

**C# (.csproj file):**
```xml
<ItemGroup>
  <!-- Update to v6.0 -->
  <PackageReference Include="Tableau.Migration" Version="6.0.*" />
</ItemGroup>
```

**Python (requirements.txt):**
```
tableau-migration>=6.0.0,<7.0.0
```

### Step 2: Update Manifest Queries

**Find and Replace (C#):**
- Replace: `manifest.GetEntries<IUser>()`
- With: `manifest.Entries.ForContentType<IUser>()`

**Find and Replace (Python):**
- Replace: `manifest.get_entries('User')`
- With: `manifest.entries.get_by_type('User')`

### Step 3: Verify Content Type Names

Ensure you're using the correct content type names:

| Content Type | C# Interface | Python String |
|--------------|-------------|---------------|
| Users | `IUser` | `'User'` |
| Groups | `IGroup` | `'Group'` |
| Projects | `IProject` | `'Project'` |
| Data Sources | `IDataSource` | `'DataSource'` |
| Workbooks | `IWorkbook` | `'Workbook'` |
| Subscriptions | `ISubscription` | `'Subscription'` |

### Step 4: Test Your Migration

Run a test migration to ensure everything works:

```bash
# C#
cd archive/csharp-examples
dotnet restore
dotnet build
dotnet run

# Python
cd TableauMigrationPython
pip install -r requirements.txt
python examples/1_basic_migration.py
```

---

## 📚 Code Examples

### Example 1: Basic Migration with v6.0 Manifest

```csharp
public async Task RunMigrationAsync()
{
    var host = Host.CreateDefaultBuilder()
        .ConfigureServices((context, services) =>
        {
            services.AddTableauMigration();
        })
        .Build();

    var migration = host.Services.GetRequiredService<IMigration>();

    var plan = migration.CreatePlanBuilder()
        .FromSourceTableauServer(
            serverUrl: new Uri("https://server.company.com"),
            siteContentUrl: "default",
            accessTokenName: "token-name",
            accessToken: "token-secret"
        )
        .ToDestinationTableauCloud(
            podUrl: new Uri("https://10ax.online.tableau.com"),
            siteContentUrl: "production",
            accessTokenName: "cloud-token",
            accessToken: "cloud-secret"
        )
        .Build();

    var result = await migration.ExecuteAsync(plan, CancellationToken.None);

    // ✅ v6.0 manifest API
    if (result.Status == MigrationCompletionStatus.Completed)
    {
        var manifest = result.Manifest;

        Console.WriteLine($"Users:         {manifest.Entries.ForContentType<IUser>().Count()}");
        Console.WriteLine($"Projects:      {manifest.Entries.ForContentType<IProject>().Count()}");
        Console.WriteLine($"Workbooks:     {manifest.Entries.ForContentType<IWorkbook>().Count()}");
        Console.WriteLine($"Subscriptions: {manifest.Entries.ForContentType<ISubscription>().Count()}");
    }
}
```

### Example 2: Analyzing Migration Results with v6.0

```csharp
public void AnalyzeMigrationResults(IMigrationResult result)
{
    var manifest = result.Manifest;

    // Get all migrated users
    var users = manifest.Entries.ForContentType<IUser>();

    // Count successful vs failed
    var successfulUsers = users.Count(u => u.Status == MigrationManifestEntryStatus.Migrated);
    var failedUsers = users.Count(u => u.Status == MigrationManifestEntryStatus.Error);

    Console.WriteLine($"✅ Successful users: {successfulUsers}");
    Console.WriteLine($"❌ Failed users: {failedUsers}");

    // Show failed entries
    foreach (var failed in users.Where(u => u.Status == MigrationManifestEntryStatus.Error))
    {
        Console.WriteLine($"Failed: {failed.Source.Name}");
        if (failed.Errors.Any())
        {
            foreach (var error in failed.Errors)
            {
                Console.WriteLine($"  Error: {error.Message}");
            }
        }
    }

    // Analyze subscriptions
    var subscriptions = manifest.Entries.ForContentType<ISubscription>();
    Console.WriteLine($"\n📧 Total subscriptions: {subscriptions.Count()}");

    // Check which subscriptions were migrated
    foreach (var sub in subscriptions)
    {
        if (sub.Destination != null)
        {
            Console.WriteLine($"✅ {sub.Source.Subject} → migrated");
        }
        else
        {
            Console.WriteLine($"❌ {sub.Source.Subject} → failed");
        }
    }
}
```

### Example 3: Exporting Manifest to CSV

```csharp
public void ExportManifestToCsv(IMigrationManifest manifest, string outputPath)
{
    using var writer = new StreamWriter(outputPath);
    using var csv = new CsvWriter(writer, CultureInfo.InvariantCulture);

    // Write header
    csv.WriteField("ContentType");
    csv.WriteField("SourceName");
    csv.WriteField("DestinationName");
    csv.WriteField("Status");
    csv.NextRecord();

    // Export users
    foreach (var user in manifest.Entries.ForContentType<IUser>())
    {
        csv.WriteField("User");
        csv.WriteField(user.Source.Name);
        csv.WriteField(user.Destination?.Name ?? "N/A");
        csv.WriteField(user.Status.ToString());
        csv.NextRecord();
    }

    // Export projects
    foreach (var project in manifest.Entries.ForContentType<IProject>())
    {
        csv.WriteField("Project");
        csv.WriteField(project.Source.Location.Name);
        csv.WriteField(project.Destination?.Location.Name ?? "N/A");
        csv.WriteField(project.Status.ToString());
        csv.NextRecord();
    }

    // Export workbooks
    foreach (var workbook in manifest.Entries.ForContentType<IWorkbook>())
    {
        csv.WriteField("Workbook");
        csv.WriteField(workbook.Source.Name);
        csv.WriteField(workbook.Destination?.Name ?? "N/A");
        csv.WriteField(workbook.Status.ToString());
        csv.NextRecord();
    }

    Console.WriteLine($"✅ Manifest exported to {outputPath}");
}
```

---

## 🎯 Common Patterns

### Pattern 1: Count Content by Type

```csharp
// v6.0 pattern
var userCount = manifest.Entries.ForContentType<IUser>().Count();
var projectCount = manifest.Entries.ForContentType<IProject>().Count();
var workbookCount = manifest.Entries.ForContentType<IWorkbook>().Count();
```

### Pattern 2: Filter Successful Migrations

```csharp
// Get only successfully migrated users
var successfulUsers = manifest.Entries
    .ForContentType<IUser>()
    .Where(u => u.Status == MigrationManifestEntryStatus.Migrated);
```

### Pattern 3: Find Failed Entries

```csharp
// Get all failed entries
var failedUsers = manifest.Entries
    .ForContentType<IUser>()
    .Where(u => u.Status == MigrationManifestEntryStatus.Error);

foreach (var failed in failedUsers)
{
    Console.WriteLine($"Failed: {failed.Source.Name}");
    foreach (var error in failed.Errors)
    {
        Console.WriteLine($"  Reason: {error.Message}");
    }
}
```

### Pattern 4: Track Source → Destination Mappings

```csharp
// See what was mapped during migration
foreach (var user in manifest.Entries.ForContentType<IUser>())
{
    Console.WriteLine($"{user.Source.Name} → {user.Destination?.Name ?? "NOT MIGRATED"}");
}
```

---

## 🐛 Troubleshooting

### Issue 1: "ForContentType method not found"

**Symptom:**
```
Error CS1061: 'IManifestEntries' does not contain a definition for 'ForContentType'
```

**Solution:**
You're using v5.x SDK. Update to v6.0:
```xml
<PackageReference Include="Tableau.Migration" Version="6.0.*" />
```

Then run:
```bash
dotnet restore
dotnet build
```

### Issue 2: Python "get_by_type not found"

**Symptom:**
```
AttributeError: 'ManifestEntries' object has no attribute 'get_by_type'
```

**Solution:**
Update to SDK v6.0:
```bash
pip install --upgrade tableau-migration>=6.0.0
```

### Issue 3: Empty Manifest Entries

**Symptom:**
```csharp
manifest.Entries.ForContentType<IUser>().Count() // Returns 0
```

**Possible Causes:**
1. Migration didn't complete successfully
2. No content of that type was migrated
3. Filters excluded all content

**Solution:**
Check migration status first:
```csharp
if (result.Status == MigrationCompletionStatus.Completed)
{
    // Then check manifest
}
else
{
    Console.WriteLine($"Migration status: {result.Status}");
    foreach (var error in result.Errors)
    {
        Console.WriteLine($"Error: {error.Message}");
    }
}
```

### Issue 4: Type Names Don't Match

**Symptom (Python):**
```python
manifest.entries.get_by_type('user')  # Returns empty
```

**Solution:**
Use PascalCase type names:
```python
manifest.entries.get_by_type('User')  # Correct
```

---

## 📖 Additional Resources

### Documentation
- [Tableau Migration SDK Documentation](https://tableau.github.io/migration-sdk/)
- [API Reference](https://tableau.github.io/migration-sdk/api/)
- [Migration Patterns](./USER_MAPPING_PATTERNS.md)

### Code Examples
- C# Examples: `archive/csharp-examples/Examples/`
- Python Examples: `TableauMigrationPython/examples/`

### Getting Help
- [GitHub Issues](https://github.com/tableau/tableau-migration-sdk/issues)
- [Community Forums](https://community.tableau.com/)

---

## ✅ Quick Reference Card

### C# v6.0 API

```csharp
// Execute migration
var result = await migration.ExecuteAsync(plan, CancellationToken.None);

// Access manifest
var manifest = result.Manifest;

// Query by type (v6.0)
manifest.Entries.ForContentType<IUser>()
manifest.Entries.ForContentType<IGroup>()
manifest.Entries.ForContentType<IProject>()
manifest.Entries.ForContentType<IDataSource>()
manifest.Entries.ForContentType<IWorkbook>()
manifest.Entries.ForContentType<ISubscription>()

// Check status
result.Status == MigrationCompletionStatus.Completed

// Get errors
result.Errors
```

### Python v6.0 API

```python
# Execute migration
result = await plan.execute_async()

# Access manifest
manifest = result.manifest

# Query by type (v6.0)
manifest.entries.get_by_type('User')
manifest.entries.get_by_type('Group')
manifest.entries.get_by_type('Project')
manifest.entries.get_by_type('DataSource')
manifest.entries.get_by_type('Workbook')
manifest.entries.get_by_type('Subscription')

# Check status
result.status == MigrationCompletionStatus.COMPLETED

# Get errors
result.errors
```

---

## 🎉 Summary

The v6.0 SDK brings improved type safety and a cleaner API for querying migration results. The key changes are:

1. **Manifest queries**: Use `ForContentType<T>()` (C#) or `get_by_type()` (Python)
2. **Type safety**: Better compile-time checking in C#
3. **Consistent API**: Unified approach across all content types
4. **Better errors**: Enhanced error reporting and diagnostics

**Migration Checklist:**
- [ ] Update package reference to v6.0
- [ ] Replace manifest query methods
- [ ] Verify content type names
- [ ] Test migration end-to-end
- [ ] Update documentation

Your code is now v6.0 compliant! 🚀
