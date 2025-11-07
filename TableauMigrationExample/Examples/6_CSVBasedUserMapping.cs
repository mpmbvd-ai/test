using Tableau.Migration;
using Tableau.Migration.Content;
using Tableau.Migration.Engine.Hooks.Mappings;
using System.Globalization;
using CsvHelper;
using CsvHelper.Configuration;

namespace TableauMigrationExample.Examples;

/// <summary>
/// Example 6: CSV-Based User Mapping
/// THE PRACTICAL APPROACH - Load user mappings from a CSV file
///
/// This is how you'll actually do migrations in real life:
/// 1. Export users from Server to CSV
/// 2. Add a column for Cloud email
/// 3. Load CSV in your migration code
/// 4. SDK uses the mappings automatically
/// </summary>

// STEP 1: Define the CSV structure
public class UserMappingRecord
{
    public string ServerUsername { get; set; } = string.Empty;
    public string CloudEmail { get; set; } = string.Empty;
    public string? Notes { get; set; }  // Optional - for your tracking
}

// STEP 2: Create mapping class that loads from CSV
public class CsvUserMapping : ContentMappingBase<IUser>
{
    private readonly Dictionary<string, string> _mappings;
    private readonly string _defaultDomain;

    // Constructor loads CSV on initialization
    public CsvUserMapping(string csvFilePath, string defaultDomain = "@company.com")
    {
        _defaultDomain = defaultDomain;
        _mappings = LoadMappingsFromCsv(csvFilePath);

        Console.WriteLine($"📄 Loaded {_mappings.Count} user mappings from CSV");
    }

    private Dictionary<string, string> LoadMappingsFromCsv(string csvPath)
    {
        var mappings = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        try
        {
            using var reader = new StreamReader(csvPath);
            using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

            var records = csv.GetRecords<UserMappingRecord>();

            foreach (var record in records)
            {
                // Skip empty rows
                if (string.IsNullOrWhiteSpace(record.ServerUsername) ||
                    string.IsNullOrWhiteSpace(record.CloudEmail))
                {
                    continue;
                }

                // Add to mapping dictionary
                mappings[record.ServerUsername.Trim()] = record.CloudEmail.Trim();
            }

            Console.WriteLine($"✓ Successfully loaded {mappings.Count} mappings");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error loading CSV: {ex.Message}");
            throw;
        }

        return mappings;
    }

    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx,
        CancellationToken cancel)
    {
        var username = ctx.ContentItem.Name;

        // Skip if already an email
        if (username.Contains("@"))
        {
            Console.WriteLine($"👤 {username} - already an email");
            return ctx;
        }

        // Check CSV mappings first
        if (_mappings.TryGetValue(username, out var email))
        {
            Console.WriteLine($"👤 {username} → {email} (from CSV)");
            return ctx.MapTo(ctx.ContentItem.Location.WithUsername(email));
        }

        // Fallback: append default domain
        var defaultEmail = $"{username}{_defaultDomain}";
        Console.WriteLine($"👤 {username} → {defaultEmail} (default)");
        return ctx.MapTo(ctx.ContentItem.Location.WithUsername(defaultEmail));
    }
}

// STEP 3: Helper to generate CSV template from Server
public class CsvMappingHelper
{
    /// <summary>
    /// Exports current Server users to CSV template
    /// You can then fill in the CloudEmail column
    /// </summary>
    public static async Task ExportUserTemplateCsv(
        string serverUrl,
        string siteContentUrl,
        string accessTokenName,
        string accessToken,
        string outputCsvPath)
    {
        Console.WriteLine("Fetching users from Tableau Server...");

        var host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                services.AddTableauMigration();
            })
            .Build();

        // Connect to source and fetch users
        var serverEndpoint = host.Services.GetRequiredService<ISourceEndpointFactory>();
        var source = await serverEndpoint.CreateAsync(
            new Uri(serverUrl),
            siteContentUrl,
            accessTokenName,
            accessToken,
            CancellationToken.None);

        var users = await source.GetUsersAsync(CancellationToken.None);

        // Write to CSV
        using var writer = new StreamWriter(outputCsvPath);
        using var csv = new CsvWriter(writer, CultureInfo.InvariantCulture);

        // Write header
        csv.WriteField("ServerUsername");
        csv.WriteField("CloudEmail");
        csv.WriteField("Notes");
        csv.NextRecord();

        // Write each user
        foreach (var user in users)
        {
            csv.WriteField(user.Name);

            // Pre-fill CloudEmail if username looks like it needs domain append
            if (!user.Name.Contains("@"))
            {
                csv.WriteField($"{user.Name}@company.com"); // They can edit this
            }
            else
            {
                csv.WriteField(user.Email); // Already an email
            }

            csv.WriteField(""); // Empty notes column
            csv.NextRecord();
        }

        Console.WriteLine($"✓ Exported {users.Count} users to {outputCsvPath}");
        Console.WriteLine($"  → Edit the CSV to fix any incorrect emails");
        Console.WriteLine($"  → Then use it in your migration");
    }
}

// STEP 4: Complete migration using CSV
public class CsvBasedMigration
{
    public async Task RunMigrationWithCsvMappingAsync()
    {
        Console.WriteLine("=================================================");
        Console.WriteLine("  CSV-BASED USER MAPPING MIGRATION");
        Console.WriteLine("=================================================\n");

        // Path to your CSV file
        var csvPath = "user_mappings.csv";

        // Validate CSV exists
        if (!File.Exists(csvPath))
        {
            Console.WriteLine($"❌ CSV file not found: {csvPath}");
            Console.WriteLine($"   Create a CSV with columns: ServerUsername,CloudEmail,Notes");
            return;
        }

        var host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                services.AddTableauMigration();

                // Register CSV mapping as a singleton with the CSV path
                services.AddSingleton<CsvUserMapping>(sp =>
                    new CsvUserMapping(csvPath, "@company.com"));
            })
            .Build();

        var migration = host.Services.GetRequiredService<IMigration>();

        Console.WriteLine("Building migration plan...\n");

        var plan = migration.CreatePlanBuilder()
            .FromSourceTableauServer(
                serverUrl: new Uri("https://tableau-server.company.com"),
                siteContentUrl: "default",
                accessTokenName: "server-token",
                accessToken: "server-secret"
            )
            .ToDestinationTableauCloud(
                podUrl: new Uri("https://10ax.online.tableau.com"),
                siteContentUrl: "production",
                accessTokenName: "cloud-token",
                accessToken: "cloud-secret"
            )
            // ⭐ Register the CSV-based mapping
            .Mappings.Add<CsvUserMapping, IUser>()
            .Build();

        Console.WriteLine("Starting migration...\n");
        var result = await migration.ExecuteAsync(plan, CancellationToken.None);

        Console.WriteLine("\n=================================================");
        Console.WriteLine("  MIGRATION RESULTS");
        Console.WriteLine("=================================================\n");

        if (result.Status == MigrationCompletionStatus.Completed)
        {
            Console.WriteLine("✅ Migration completed successfully!\n");

            var manifest = result.Manifest;
            Console.WriteLine($"📊 Users migrated: {manifest.Entries.ForContentType<IUser>().Count()}");
            Console.WriteLine($"📊 Subscriptions migrated: {manifest.Entries.ForContentType<ISubscription>().Count()}\n");
        }
        else
        {
            Console.WriteLine($"❌ Migration failed: {result.Status}\n");
            foreach (var error in result.Errors)
            {
                Console.WriteLine($"   Error: {error.Message}");
            }
        }

        Console.WriteLine("=================================================\n");
    }
}

/*
 * YOUR WORKFLOW:
 *
 * STEP 1: Export users from Server to CSV
 * ----------------------------------------
 * Option A - From Tableau Server Admin UI:
 * 1. Sign in to Tableau Server
 * 2. Go to Users page
 * 3. Export list to CSV
 *
 * Option B - Using this helper (recommended):
 * CsvMappingHelper.ExportUserTemplateCsv(
 *     "https://tableau-server.company.com",
 *     "default",
 *     "token-name",
 *     "token-secret",
 *     "user_mappings.csv"
 * );
 *
 * This creates a CSV like:
 * ServerUsername,CloudEmail,Notes
 * jsmith,jsmith@company.com,
 * ajones,ajones@company.com,
 * admin,admin@company.com,
 *
 * STEP 2: Edit the CSV
 * --------------------
 * Open user_mappings.csv in Excel/Google Sheets:
 *
 * ServerUsername | CloudEmail                  | Notes
 * ---------------|-----------------------------|------------------
 * jsmith         | john.smith@company.com      | Full name needed
 * ajones         | alice.jones@company.com     | Full name needed
 * admin          | admin.tableau@company.com   | Special account
 * bwilson        | bob.wilson@company.com      | OK as-is
 *
 * Fix the CloudEmail column for each user.
 *
 * STEP 3: Save and use in migration
 * ----------------------------------
 * var mapping = new CsvUserMapping("user_mappings.csv");
 * plan.Mappings.Add<CsvUserMapping, IUser>()
 *
 * STEP 4: Run migration
 * ---------------------
 * The SDK automatically:
 * 1. Loads mappings from CSV
 * 2. Migrates users with correct emails
 * 3. Updates all subscription references
 *
 * ADVANTAGES OF CSV APPROACH:
 *
 * ✅ Easy to review - open in Excel
 * ✅ Easy to edit - no code changes needed
 * ✅ Team collaboration - share CSV for review
 * ✅ Reusable - save for future migrations
 * ✅ Auditable - track what was mapped
 * ✅ Version control - commit CSV to git
 * ✅ Can add notes/comments
 *
 * CSV FORMAT REQUIREMENTS:
 *
 * Required columns:
 * - ServerUsername: Username from Tableau Server
 * - CloudEmail: Email address for Tableau Cloud
 *
 * Optional columns:
 * - Notes: Any comments/tracking info
 * - Department, Manager, etc.: Additional metadata
 *
 * The code only uses ServerUsername and CloudEmail.
 *
 * EXAMPLE CSV CONTENT:
 *
 * ServerUsername,CloudEmail,Notes
 * jsmith,john.smith@company.com,Sales Manager
 * ajones,alice.jones@company.com,Marketing Director
 * bwilson,bob.wilson@company.com,
 * admin,admin.tableau@company.com,Admin account - do not delete
 * svc_tableau,svc.tableau@company.com,Service account for extracts
 *
 * HANDLING ERRORS:
 *
 * If a user in Server isn't in the CSV:
 * - Falls back to appending default domain
 * - Example: "newuser" → "newuser@company.com"
 *
 * If CloudEmail is invalid:
 * - Migration will fail for that user
 * - Check logs to see which user
 * - Fix CSV and re-run
 *
 * TESTING YOUR CSV:
 *
 * 1. Create a small test CSV with 5-10 users
 * 2. Run migration to test Cloud site
 * 3. Verify users created correctly
 * 4. Check subscriptions work
 * 5. Then use full CSV for production
 *
 * PRO TIPS:
 *
 * 1. Add a "Status" column to track migration progress
 * 2. Keep original export for reference
 * 3. Use Excel formulas to generate CloudEmail from ServerUsername
 *    Example: =A2&"@company.com"
 * 4. Highlight rows that need manual review
 * 5. Save multiple versions as you iterate
 */
