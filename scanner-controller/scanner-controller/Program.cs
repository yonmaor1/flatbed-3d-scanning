// See https://aka.ms/new-console-template for more information

using NAPS2.Images.Wpf;
using NAPS2.Images.Mac;
using NAPS2.Images.Gtk;
using NAPS2.Scan;
using NAPS2.Images;
using NAPS2.Scan.Exceptions;
using Gtk;


// Set up the scanning context
// windows check
ScanningContext scanningContext;
if (OperatingSystem.IsWindows() && OperatingSystem.IsWindowsVersionAtLeast(7))
{
    Console.WriteLine("Windows");
    scanningContext = new ScanningContext(new WpfImageContext());
}
// May have to create separate files for supporting mac or linux?
// else if mac, set it up
else if (OperatingSystem.IsMacOS())
{
    scanningContext = new ScanningContext(new MacImageContext());
}
// else if linux, set it up
else if (OperatingSystem.IsLinux())
{
    Console.WriteLine("Linux");
    // scanningContext = new ScanningContext(new GtkImageContext());
    scanningContext = new ScanningContext(new WpfImageContext());
}
else 
{
    throw new PlatformNotSupportedException("This platform is not supported.");
}

var controller = new ScanController(scanningContext);

// Query for available scanning devices
var devices = await controller.GetDeviceList();

if (devices.Count == 0)
{
    throw new Exception("No scanners found.");
}

// Set scanning options
var options = new ScanOptions
{
    Device = devices.First(),
    PaperSource = PaperSource.Flatbed,
    PageSize = PageSize.A4,
    Dpi = 150,
};

// ScanDevice device = (await controller.GetDeviceList()).First();
//var options = new ScanOptions { Device = device };

// get what number scan cycle this is
// int scanID = 0;
// for (int i = 0; i < 1000; i++)
// {
//     if (!Directory.Exists($"scans/scan{i}"))
//     {
//         scanID = i;
//         break;
//     }
// }

// Console.WriteLine(scanID);

// create new folder in existing scans folder for this scan cycle
// Directory.CreateDirectory("scans/scan" + scanID);
// Directory.SetCurrentDirectory("scans/scan" + scanID);

// Scan and save images
// send out .png format images
int scanNumber = 1;

// scan and save images allowing up to a minute for each scan
await foreach (var image in controller.Scan(options))
{
    image.Save($"scanPage{scanNumber++}.png");
    Console.WriteLine($"Saved scanPage{scanNumber - 1}.png");
}

Console.WriteLine("Completed scanning process.");
