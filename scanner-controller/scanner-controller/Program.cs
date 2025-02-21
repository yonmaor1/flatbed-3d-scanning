// See https://aka.ms/new-console-template for more information

using NAPS2.Images.Wpf;
using NAPS2.Images.Mac;
using NAPS2.Images.Gtk;
using NAPS2.Scan;
using NAPS2.Images;
using NAPS2.Scan.Exceptions;

// Set up the scanning context
// windows check
ScanningContext scanningContext;
if (OperatingSystem.IsWindows() && OperatingSystem.IsWindowsVersionAtLeast(7))
{
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
    PaperSource = PaperSource.Feeder,
    PageSize = PageSize.A4,
    Dpi = 4800
};

// get what number scan cycle this is
int scanCycle = 0;
for (int i = 0; i < 1000; i++)
{
    if (!Directory.Exists($"scans/scan{i}"))
    {
        scanCycle = i;
        break;
    }
}

// create new folder in existing scans folder for this scan cycle
Directory.CreateDirectory("scans/scan" + scanCycle);
Directory.SetCurrentDirectory("scans/scan" + scanCycle);

// Scan and save images
// send out .png format images
int scanNumber = 1;
await foreach (var image in controller.Scan(options))
{
    image.Save($"scanPage{scanNumber++}.png");
}


Console.WriteLine("Hello, World!");
