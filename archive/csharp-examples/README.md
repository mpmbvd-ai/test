# Tableau Migration SDK v6.0 - C# Examples

This project contains complete C# examples for using **Tableau Migration SDK v6.0** to migrate content from Tableau Server to Tableau Cloud.

## 🚀 Quick Start

### Prerequisites
- .NET 8.0 SDK or later
- Tableau Server access (source)
- Tableau Cloud access (destination)
- Access tokens for both source and destination

### Installation

```bash
# Navigate to the project directory
cd archive/csharp-examples

# Restore packages (includes Tableau.Migration v6.0)
dotnet restore

# Build the project
dotnet build
```

### Running Examples

1. Open `Program.cs`
2. Uncomment one of the examples
3. Update credentials in the example file
4. Run: `dotnet run`

## 📚 Examples Overview

| Example | File | Description |
|---------|------|-------------|
| 1️⃣ Basic Setup | `1_BasicMigrationSetup.cs` | Minimal migration with no mapping |
| 2️⃣ Project Mapping | `2_ProjectMappingExample.cs` | Rename projects during migration |
| 3️⃣ User Mapping | `3_UserMappingForSubscriptions.cs` | Change email domains |
| 4️⃣ Complete Migration | `4_CompleteSubscriptionMigration.cs` | Production-ready example |
| 5️⃣ Username → Email | `5_UsernameToEmailMapping.cs` | **Most common scenario** |
| 6️⃣ CSV Mapping | `6_CSVBasedUserMapping.cs` | **Recommended for production** |

See [Examples/README.md](Examples/README.md) for detailed information about each example.

## 🆕 SDK v6.0 Features

This project uses **Tableau Migration SDK v6.0** with these key improvements:

### v6.0 Manifest API

```csharp
// Execute migration
var result = await migration.ExecuteAsync(plan, CancellationToken.None);

// Access manifest (v6.0 API)
var manifest = result.Manifest;

// Query entries by type - v6.0 pattern ✅
var users = manifest.Entries.ForContentType<IUser>();
var projects = manifest.Entries.ForContentType<IProject>();
var workbooks = manifest.Entries.ForContentType<IWorkbook>();
var subscriptions = manifest.Entries.ForContentType<ISubscription>();

// Count migrated content
Console.WriteLine($"Users: {manifest.Entries.ForContentType<IUser>().Count()}");
```

### What Changed from v5.x?

| v5.x (Old) | v6.0 (New) |
|------------|------------|
| `manifest.GetEntries<T>()` | `manifest.Entries.ForContentType<T>()` |
| `manifest.Entries.OfType<T>()` | `manifest.Entries.ForContentType<T>()` |

**Migration Guide:** [docs/V6_MIGRATION_GUIDE.md](../../docs/V6_MIGRATION_GUIDE.md)

**Quick Reference:** [docs/V6_QUICK_REFERENCE.md](../../docs/V6_QUICK_REFERENCE.md)

## 🔑 Key Concepts

### 1. Subscriptions Migrate Automatically
When you migrate workbooks with user mapping, subscriptions are automatically migrated and user references are updated.

```
Source: alice@old.com subscribed to "Report"
Mapping: alice@old.com → alice@new.com
Result: alice@new.com subscribed to "Report" ✅
```

### 2. Mapping is the Key
Define how content should be renamed/mapped during migration:
- **Project mapping**: Rename projects
- **User mapping**: Change email domains or usernames

### 3. CSV-Based Mapping is Recommended
For production migrations, use CSV files for user mappings:
- Easy to review in Excel/Google Sheets
- Non-developers can edit
- Version control friendly
- Reusable

## 📖 Documentation

- **v6.0 Migration Guide**: [docs/V6_MIGRATION_GUIDE.md](../../docs/V6_MIGRATION_GUIDE.md)
- **v6.0 Quick Reference**: [docs/V6_QUICK_REFERENCE.md](../../docs/V6_QUICK_REFERENCE.md)
- **Example Details**: [Examples/README.md](Examples/README.md)
- **User Mapping Patterns**: [docs/USER_MAPPING_PATTERNS.md](../../docs/USER_MAPPING_PATTERNS.md)

## 🎯 Recommended Workflow

1. **Start with Example 1** - Understand the basic structure
2. **Study Example 5** - Username to email mapping (most common)
3. **Use Example 6** - CSV-based mapping for production
4. **Test on a test Cloud site** - Before production migration
5. **Review manifest** - Verify what was migrated
6. **Expand to full migration** - Once confident

## 🔧 Project Structure

```
archive/csharp-examples/
├── TableauMigrationExample.csproj  # v6.0 SDK reference
├── Program.cs                       # Main entry point
├── Examples/
│   ├── 1_BasicMigrationSetup.cs
│   ├── 2_ProjectMappingExample.cs
│   ├── 3_UserMappingForSubscriptions.cs
│   ├── 4_CompleteSubscriptionMigration.cs
│   ├── 5_UsernameToEmailMapping.cs
│   └── 6_CSVBasedUserMapping.cs
└── README.md
```

## ⚠️ Important Notes

### Before Production Migration:
- ✅ Test on a test Cloud site first
- ✅ Start with a small subset of content
- ✅ Review user mappings carefully
- ✅ Verify subscriptions work after migration
- ✅ Keep backup of source data

### Common Scenarios:
- **Server → Cloud**: Most common, requires username → email mapping
- **Domain change**: User email domains change during migration
- **Project rename**: Consolidate multiple Server sites to Cloud
- **Subscription migration**: Automatically handled by SDK

## 🐛 Troubleshooting

### "ForContentType not found" error
**Solution:** Ensure you're using SDK v6.0:
```bash
dotnet restore
dotnet build
```

### Empty manifest entries
**Check:**
1. Migration completed successfully?
2. Any errors in `result.Errors`?
3. Filters excluding content?

### Subscriptions not migrating
**Verify:**
1. User mapping is correct
2. Users exist in destination
3. Workbooks migrated successfully

See [V6_MIGRATION_GUIDE.md](../../docs/V6_MIGRATION_GUIDE.md) for more troubleshooting.

## 📞 Getting Help

- **GitHub Issues**: https://github.com/tableau/tableau-migration-sdk/issues
- **Documentation**: https://tableau.github.io/migration-sdk/
- **Community**: https://community.tableau.com/

## ✅ Version Information

- **SDK Version**: 6.0.x
- **.NET Version**: 8.0
- **Last Updated**: March 2026

---

**Ready to migrate?** Start with [Examples/README.md](Examples/README.md) 🚀
