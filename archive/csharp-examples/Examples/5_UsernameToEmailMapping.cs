using Tableau.Migration;
using Tableau.Migration.Content;
using Tableau.Migration.Engine.Hooks.Mappings;

namespace TableauMigrationExample.Examples;

/// <summary>
/// Example 5: Username to Email Mapping
/// THE MOST COMMON CLOUD MIGRATION SCENARIO
///
/// Server uses simple usernames: "john.smith", "alice.jones"
/// Cloud requires email addresses: "john.smith@company.com", "alice.jones@company.com"
///
/// This mapping is CRITICAL for subscriptions to work!
/// </summary>

// APPROACH 1: Simple domain append
public class UsernameToEmailMapping : ContentMappingBase<IUser>
{
    private const string EmailDomain = "@company.com";

    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx,
        CancellationToken cancel)
    {
        var user = ctx.ContentItem;
        var username = user.Name;

        Console.WriteLine($"👤 Processing user: {username}");

        // Check if it's already an email (might have @ symbol)
        if (username.Contains("@"))
        {
            Console.WriteLine($"   ✓ Already an email: {username}");
            return ctx; // Already an email, no change needed
        }

        // Convert username to email by appending domain
        var email = $"{username}{EmailDomain}";
        Console.WriteLine($"   📧 Converting: {username} → {email}");

        // Map to new email address
        return ctx.MapTo(user.Location.WithUsername(email));
    }
}

// APPROACH 2: Username lookup table (for non-standard mappings)
public class UsernameLookupMapping : ContentMappingBase<IUser>
{
    // Some usernames don't map directly - they need a lookup table
    private static readonly Dictionary<string, string> UsernameMappings = new()
    {
        // Format: { "Server Username", "Cloud Email" }
        { "jsmith", "john.smith@company.com" },          // Abbreviated username
        { "ajones", "alice.jones@company.com" },         // Abbreviated username
        { "bob.wilson", "robert.wilson@company.com" },   // Different first name
        { "admin", "admin.tableau@company.com" },        // Special accounts
        { "service_account", "svc.tableau@company.com" } // Service accounts
    };

    private const string DefaultDomain = "@company.com";

    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx,
        CancellationToken cancel)
    {
        var user = ctx.ContentItem;
        var username = user.Name;

        // Skip if already an email
        if (username.Contains("@"))
        {
            return ctx;
        }

        // First, check lookup table for specific mappings
        if (UsernameMappings.TryGetValue(username, out var mappedEmail))
        {
            Console.WriteLine($"👤 Lookup mapping: {username} → {mappedEmail}");
            return ctx.MapTo(user.Location.WithUsername(mappedEmail));
        }

        // Otherwise, append default domain
        var defaultEmail = $"{username}{DefaultDomain}";
        Console.WriteLine($"👤 Default mapping: {username} → {defaultEmail}");
        return ctx.MapTo(user.Location.WithUsername(defaultEmail));
    }
}

// APPROACH 3: Configuration-based mapping (most flexible)
public class ConfigurableUsernameToEmailMapping : ContentMappingBase<IUser>
{
    private readonly string _emailDomain;
    private readonly Dictionary<string, string> _specialMappings;

    // Constructor receives configuration
    public ConfigurableUsernameToEmailMapping(
        string emailDomain,
        Dictionary<string, string>? specialMappings = null)
    {
        _emailDomain = emailDomain;
        _specialMappings = specialMappings ?? new Dictionary<string, string>();
    }

    public override async Task<ContentMappingContext<IUser>?> MapAsync(
        ContentMappingContext<IUser> ctx,
        CancellationToken cancel)
    {
        var user = ctx.ContentItem;
        var username = user.Name;

        // Already an email?
        if (username.Contains("@"))
        {
            return ctx;
        }

        // Check special mappings first
        if (_specialMappings.TryGetValue(username, out var specialEmail))
        {
            Console.WriteLine($"👤 Special: {username} → {specialEmail}");
            return ctx.MapTo(user.Location.WithUsername(specialEmail));
        }

        // Default: append domain
        var email = $"{username}{_emailDomain}";
        Console.WriteLine($"👤 Standard: {username} → {email}");
        return ctx.MapTo(user.Location.WithUsername(email));
    }
}

// COMPLETE EXAMPLE: Migration with Username → Email mapping
public class ServerToCloudUsernameMigration
{
    public async Task RunMigrationAsync()
    {
        Console.WriteLine("=================================================");
        Console.WriteLine("  SERVER USERNAME → CLOUD EMAIL MIGRATION");
        Console.WriteLine("=================================================\n");

        var host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                services.AddTableauMigration();
            })
            .Build();

        var migration = host.Services.GetRequiredService<IMigration>();

        Console.WriteLine("Building migration plan...\n");

        var plan = migration.CreatePlanBuilder()
            // SOURCE: Tableau Server (uses simple usernames)
            .FromSourceTableauServer(
                serverUrl: new Uri("https://tableau-server.company.com"),
                siteContentUrl: "default",
                accessTokenName: "server-token",
                accessToken: "server-secret"
            )
            // DESTINATION: Tableau Cloud (requires email addresses)
            .ToDestinationTableauCloud(
                podUrl: new Uri("https://10ax.online.tableau.com"),
                siteContentUrl: "production",
                accessTokenName: "cloud-token",
                accessToken: "cloud-secret"
            )
            // ⭐ KEY: Register username → email mapping
            .Mappings.Add<UsernameLookupMapping, IUser>()
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
 * REAL-WORLD SCENARIO:
 *
 * SOURCE (Tableau Server - Simple Usernames):
 * ├── Users:
 * │   ├── jsmith            ← Just a username
 * │   ├── ajones            ← Just a username
 * │   └── bob.wilson        ← Just a username
 * ├── Workbook: "Sales Dashboard"
 * └── Subscriptions:
 *     ├── jsmith → "Sales Dashboard" (Every Monday)
 *     └── ajones → "Sales Dashboard" (Every Friday)
 *
 * WITHOUT MAPPING (Migration would fail!):
 * Cloud sees: "jsmith"
 * Cloud says: ❌ Invalid user - not an email address!
 *
 * WITH MAPPING (Migration succeeds!):
 *
 * DESTINATION (Tableau Cloud - Email Addresses):
 * ├── Users:
 * │   ├── john.smith@company.com    ← Mapped from "jsmith"
 * │   ├── alice.jones@company.com   ← Mapped from "ajones"
 * │   └── robert.wilson@company.com ← Mapped from "bob.wilson"
 * ├── Workbook: "Sales Dashboard"
 * └── Subscriptions:
 *     ├── john.smith@company.com → "Sales Dashboard" (Every Monday)
 *     └── alice.jones@company.com → "Sales Dashboard" (Every Friday)
 *
 * WHAT THE SDK DOES:
 * 1. Reads user "jsmith" from Server
 * 2. Applies mapping: "jsmith" → "john.smith@company.com"
 * 3. Creates user "john.smith@company.com" in Cloud
 * 4. Reads subscription for "jsmith"
 * 5. Looks up mapping: "jsmith" → "john.smith@company.com"
 * 6. Creates subscription for "john.smith@company.com" in Cloud
 *
 * THE SUBSCRIPTION AUTOMATICALLY USES THE MAPPED EMAIL!
 *
 * COMMON PATTERNS:
 *
 * Pattern 1: Simple append
 * "john.smith" → "john.smith@company.com"
 * Use: UsernameToEmailMapping
 *
 * Pattern 2: Abbreviated usernames
 * "jsmith" → "john.smith@company.com"
 * Use: UsernameLookupMapping with dictionary
 *
 * Pattern 3: Mixed
 * Most users: append domain
 * Special cases: lookup table
 * Use: UsernameLookupMapping (checks table first, then appends)
 *
 * TESTING YOUR MAPPINGS:
 *
 * 1. Export users from Server (CSV)
 * 2. Create mapping table:
 *    Server Username → Expected Cloud Email
 * 3. Build dictionary in code
 * 4. Test with small subset first
 * 5. Verify subscriptions work in Cloud
 *
 * IMPORTANT NOTES:
 *
 * - Cloud REQUIRES email addresses (RFC 5322 compliant)
 * - Server can use any string as username
 * - Mapping MUST happen during migration
 * - Subscriptions depend on correct user mapping
 * - Test your mapping rules before full migration!
 *
 * TROUBLESHOOTING:
 *
 * Problem: User "jsmith" can't login to Cloud
 * Solution: Cloud uses email for login, not username
 *           Users login as "john.smith@company.com"
 *
 * Problem: Subscription not found for user
 * Solution: User mapping might be wrong
 *           Check logs to see what email was used
 *
 * Problem: Some users work, others don't
 * Solution: Mixed username formats on Server
 *           Use lookup table for exceptions
 */
