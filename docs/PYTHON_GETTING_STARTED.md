# Getting Started with Tableau Migration SDK - Python Edition

## What We Built (Python Version)

Everything from the C# examples, now in **clean, simple Python**!

Complete Python examples for subscription migration with user/project mapping.

---

## 📁 Python Files

### Main Python Project
**Location:** `TableauMigrationPython/`

**Key Files:**
- `requirements.txt` - Just one dependency: `tableau-migration`
- `README.md` - Complete Python guide
- `user_mappings_template.csv` - Sample CSV format
- `examples/` - 6 progressive Python examples

### Python Examples (examples/ folder)

**1_basic_migration_setup.py**
- Simplest possible migration
- Understand the basic structure
- See how async/await works

**2_project_mapping.py**
- Rename projects during migration
- Dictionary-based rules
- Automatic workbook relocation

**3_user_mapping_for_subscriptions.py**
- Email domain changes
- Specific user overrides
- Critical for subscriptions

**4_username_to_email_mapping.py** ⭐ **MOST COMMON**
- Server usernames → Cloud emails
- "jsmith" → "john.smith@company.com"
- Lookup table approach

**5_csv_based_user_mapping.py** ⭐ **PRODUCTION APPROACH**
- Load mappings from CSV
- No hardcoding needed
- Team-friendly workflow
- **Use this 95% of the time!**

**6_complete_subscription_migration.py** ⭐ **COMPLETE EXAMPLE**
- Everything together
- Production-ready
- CSV mapping + project mapping + filtering
- Your starting template

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install (2 minutes)

```bash
cd TableauMigrationPython

# Install the SDK
pip install -r requirements.txt

# Or directly:
pip install tableau-migration
```

### Step 2: Try an Example (5 minutes)

```bash
# Start with Example 1 to see the structure
python examples/1_basic_migration_setup.py

# Try Example 5 (CSV-based - most practical)
python examples/5_csv_based_user_mapping.py
```

### Step 3: Customize for Your Environment (30 minutes)

1. **Create your CSV:**
   ```csv
   ServerUsername,CloudEmail,Notes
   jsmith,john.smith@company.com,Abbreviated
   ajones,alice.jones@company.com,Abbreviated
   ```

2. **Edit Example 6:**
   - Update server URL and credentials
   - Update Cloud URL and credentials
   - Update project mappings dict
   - Point to your CSV file

3. **Test with small subset first!**

---

## 💡 Why Python is Better

| Aspect | Python | C# |
|--------|--------|-----|
| **Installation** | `pip install tableau-migration` | NuGet + DI setup |
| **Code** | Clean, minimal boilerplate | More verbose |
| **CSV** | Built-in `csv` module | Requires CsvHelper |
| **Learning** | Easier if you know Python | Need to know .NET |
| **Testing** | Quick iteration | Longer compile/run cycle |

**Same SDK power, simpler code!**

---

## 📝 What You Need to Provide

### For User Mapping (95% of cases):

**Just a CSV file:**
```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
ajones,alice.jones@company.com
admin,admin.tableau@company.com
```

**That's it!** The SDK does everything else.

### For Project Mapping:

**Just a Python dict:**
```python
PROJECT_MAPPINGS = {
    "Marketing": "Cloud - Marketing",
    "Sales": "Cloud - Sales"
}
```

---

## 🎯 Your Workflow

```
1. Export users from Server
   ↓
2. Create CSV with ServerUsername,CloudEmail columns
   ↓
3. Edit CSV in Excel (use formulas to auto-fill!)
   ↓
4. Save as user_mappings.csv
   ↓
5. Run Python script
   ↓
6. Subscriptions automatically work! ✅
```

---

## 📚 Documentation (Still Applies!)

All the conceptual docs still apply - they're language-agnostic:

**SUBSCRIPTIONS_AND_MAPPING.md** ⭐ **START HERE**
- How subscriptions work
- Why mapping is critical
- Real-world examples

**USER_MAPPING_PATTERNS.md**
- 5 common username→email scenarios
- Building your mapping strategy
- Troubleshooting guide

**CSV_MAPPING_WORKFLOW.md**
- Complete CSV workflow
- Excel tips and formulas
- Testing strategies

---

## 🔍 How It Works (Python Example)

```python
from tableau_migration import PyUser
from tableau_migration.migration import PyMigrationPlanBuilder
import csv

# STEP 1: Load CSV mappings
class CsvUserMapping:
    def __init__(self, csv_path):
        self.mappings = {}
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.mappings[row['ServerUsername']] = row['CloudEmail']

    def map(self, ctx):
        username = ctx.content_item.name
        if username in self.mappings:
            email = self.mappings[username]
            return ctx.map_to(ctx.content_item.location.with_username(email))
        return ctx

# STEP 2: Build migration plan
plan_builder = PyMigrationPlanBuilder()

plan_builder = (
    plan_builder
    .from_source_tableau_server(...)
    .to_destination_tableau_cloud(...)
)

# STEP 3: Add CSV mapping
csv_mapping = CsvUserMapping("user_mappings.csv")
plan_builder.mappings.add(csv_mapping)

# STEP 4: Run migration
plan = plan_builder.build()
result = await plan.execute_async()

# DONE! Subscriptions automatically updated!
```

**See? Much simpler than C#!**

---

## 🎓 Learning Path

### Day 1: Understand Concepts (30 minutes)
1. Read `SUBSCRIPTIONS_AND_MAPPING.md`
2. Understand the migration pipeline
3. See how mapping works

### Day 2: Study Python Examples (1 hour)
1. Read `TableauMigrationPython/README.md`
2. Study examples 1→2→3→4→5
3. Run Example 1 to see it work

### Day 3: Create Your CSV (1 hour)
1. Export users from your Server
2. Create CSV with ServerUsername,CloudEmail
3. Use Excel formulas to auto-fill
4. Manually fix abbreviated usernames
5. Save as `user_mappings.csv`

### Day 4: Test Migration (2 hours)
1. Create test CSV with 5-10 users
2. Set up test Cloud site
3. Run Example 5 or 6 with test data
4. Verify users, projects, subscriptions
5. Check subscription emails work

### Day 5: Production (When Ready)
1. Use full CSV
2. Review with team
3. Run migration
4. Monitor and validate
5. Done!

---

## ✅ Common Scenarios (Python Solutions)

### Scenario 1: Simple username → email

**Server:** `john.smith`
**Cloud:** `john.smith@company.com`

**Solution:**
```python
class SimpleMapping:
    def map(self, ctx):
        username = ctx.content_item.name
        if "@" not in username:
            email = f"{username}@company.com"
            return ctx.map_to(ctx.content_item.location.with_username(email))
        return ctx
```

---

### Scenario 2: Abbreviated usernames (CSV)

**Server:** `jsmith`, `ajones`
**Cloud:** `john.smith@company.com`, `alice.jones@company.com`

**Solution:** Use CSV!
```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
ajones,alice.jones@company.com
```

**Code:**
```python
csv_mapping = CsvUserMapping("user_mappings.csv")
plan_builder.mappings.add(csv_mapping)
```

---

### Scenario 3: Project aggregation

**Server:** Multiple sites with "Marketing", "Sales"
**Cloud:** Single site with "Cloud - Marketing", "Cloud - Sales"

**Solution:**
```python
class CloudProjectMapping:
    PROJECT_MAPPINGS = {
        "Marketing": "Cloud - Marketing",
        "Sales": "Cloud - Sales",
        "Finance": "Cloud - Finance"
    }

    def map(self, ctx):
        name = ctx.content_item.location.name
        if name in self.PROJECT_MAPPINGS:
            new_name = self.PROJECT_MAPPINGS[name]
            return ctx.map_to(ctx.content_item.location.rename(new_name))
        return ctx

plan_builder.mappings.add(CloudProjectMapping())
```

---

## 🐛 Troubleshooting

### "tableau_migration not found"
```bash
pip install tableau-migration
```

### "CSV file not found"
Create `user_mappings.csv` in the same folder as your script:
```csv
ServerUsername,CloudEmail
jsmith,john.smith@company.com
```

### Subscriptions not working
1. Check user mapping is correct
2. Verify Cloud users have correct emails
3. Check migration logs for errors
4. Test one subscription manually

### "Invalid email format"
Cloud requires emails with @. Check your CSV - all CloudEmail values must contain @.

---

## 📊 What Gets Migrated Automatically

When you map users and projects, the SDK automatically updates:

✅ **Users** (with your mappings)
✅ **Groups** (with updated user memberships)
✅ **Projects** (with your name mappings)
✅ **Data Sources** (moved to new projects)
✅ **Workbooks** (moved to new projects)
✅ **Subscriptions** ← **References updated automatically!**
✅ **Extract Refresh Tasks**
✅ **Permissions** (updated for new users/projects)

**You never touch subscriptions directly!**

---

## 🎯 Key Takeaways

1. **Python is simpler** than C# for this use case
2. **CSV approach is best** for production (you said 95% of the time)
3. **Subscriptions migrate automatically** when you map users
4. **Test first** before production
5. **SDK handles complexity** - you just provide rules

---

## 📦 What You Have Now

```
TableauMigrationPython/
├── README.md                          ← Complete Python guide
├── requirements.txt                   ← Just: tableau-migration
├── user_mappings_template.csv         ← Sample CSV format
└── examples/
    ├── 1_basic_migration_setup.py    ← Learn the basics
    ├── 2_project_mapping.py          ← Rename projects
    ├── 3_user_mapping_for_subscriptions.py
    ├── 4_username_to_email_mapping.py ← Most common scenario
    ├── 5_csv_based_user_mapping.py   ← Use this 95% of time!
    └── 6_complete_subscription_migration.py ← Production template
```

Plus all the language-agnostic docs:
- `SUBSCRIPTIONS_AND_MAPPING.md`
- `USER_MAPPING_PATTERNS.md`
- `CSV_MAPPING_WORKFLOW.md`

---

## 🚀 Next Steps

1. **Install:** `pip install tableau-migration`
2. **Read:** `TableauMigrationPython/README.md`
3. **Try:** `python examples/1_basic_migration_setup.py`
4. **Read:** `SUBSCRIPTIONS_AND_MAPPING.md` for concepts
5. **Create:** Your `user_mappings.csv`
6. **Run:** `python examples/5_csv_based_user_mapping.py`
7. **Test:** With small subset first
8. **Production:** When ready!

---

## Summary

**Python Edition = Same Power, Less Code**

You provide:
- CSV with user mappings (95% of the time)
- Dict with project mappings (simple Python dict)

SDK does:
- ✅ Migrates everything
- ✅ Updates all references
- ✅ Handles subscriptions automatically
- ✅ Reports results

**Start with Example 5 (CSV-based) - it's what you'll use in production!**
