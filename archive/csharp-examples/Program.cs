using TableauMigrationExample.Examples;

/*
 * =====================================================================
 *  TABLEAU MIGRATION SDK v6.0 - Example Runner
 * =====================================================================
 *
 * This project demonstrates how to use Tableau Migration SDK v6.0
 * to migrate content from Tableau Server to Tableau Cloud.
 *
 * WHAT'S NEW IN v6.0:
 * - Improved manifest API: result.Manifest.Entries.ForContentType<T>()
 * - Better type safety for content queries
 * - Enhanced migration result tracking
 * - Streamlined plan builder API
 *
 * =====================================================================
 */

Console.WriteLine("╔═══════════════════════════════════════════════════════════╗");
Console.WriteLine("║   TABLEAU MIGRATION SDK v6.0 - C# EXAMPLES              ║");
Console.WriteLine("╚═══════════════════════════════════════════════════════════╝");
Console.WriteLine();

// Uncomment the example you want to run:

// EXAMPLE 1: Basic migration setup (no mapping)
// var example = new BasicMigrationSetup();
// await example.RunMigrationAsync();

// EXAMPLE 2: Project mapping (rename projects)
// var example = new ProjectMappingExample();
// await example.RunMigrationWithProjectMappingAsync();

// EXAMPLE 3: User mapping with email domain change
// var example = new UserMappingExample();
// await example.RunMigrationWithUserMappingAsync();

// EXAMPLE 4: Complete subscription migration (projects + users)
// var example = new CompleteSubscriptionMigration();
// await example.RunCompleteSubscriptionMigrationAsync();

// EXAMPLE 5: Username to email mapping (Server → Cloud)
// var example = new ServerToCloudUsernameMigration();
// await example.RunMigrationAsync();

// EXAMPLE 6: CSV-based user mapping (recommended for production)
// var example = new CsvBasedMigration();
// await example.RunMigrationWithCsvMappingAsync();

Console.WriteLine();
Console.WriteLine("📚 To run an example:");
Console.WriteLine("   1. Uncomment one of the examples above in Program.cs");
Console.WriteLine("   2. Update credentials in the example file");
Console.WriteLine("   3. Run: dotnet run");
Console.WriteLine();
Console.WriteLine("🔑 v6.0 KEY FEATURES:");
Console.WriteLine("   ✓ Type-safe manifest queries: manifest.Entries.ForContentType<IUser>()");
Console.WriteLine("   ✓ Improved result tracking: result.Manifest, result.Status, result.Errors");
Console.WriteLine("   ✓ Automatic subscription mapping when users are mapped");
Console.WriteLine("   ✓ Enhanced error reporting and logging");
Console.WriteLine();
Console.WriteLine("📖 For more information, see: docs/V6_MIGRATION_GUIDE.md");
Console.WriteLine();
