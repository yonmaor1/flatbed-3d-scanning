﻿// See https://aka.ms/new-console-template for more information

using NAPS2.Images.Gdi;
using NAPS2.Images.Mac;
using NAPS2.Images.Gtk;
using NAPS2.Scan;
using NAPS2.Images;

ScanningContext scanningContext;

// windows check
if (OperatingSystem.IsWindows() && OperatingSystem.IsWindowsVersionAtLeast(7))
{
    scanningContext = new ScanningContext(new GdiImageContext());
}
// else if mac, set it up
else if (OperatingSystem.IsMacOS())
{
    Console.WriteLine("Mac");
    scanningContext = new ScanningContext(new MacImageContext());
}
// else if linux, set it up
else if (OperatingSystem.IsLinux())
{
    scanningContext = new ScanningContext(new GtkImageContext());
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
    Dpi = 100,
};

// get what number scan cycle this is
int scanID = 0;
for (int i = 0; i < 50; i++)
{
    // if doesn't exist, break
    if (!Directory.Exists("scans/scan" + i))
    {
        break;
    }
    scanID = i;
}

// go to correct scan directory
Directory.SetCurrentDirectory("scans/scan" + scanID);

// find scan number
int scanNumber = 0;
for (int i = 0; i < 50; i++)
{
    // if scan page does not exist, update and break
    if (!File.Exists($"scanPage_{i*90}.png"))
    {
        // name for angle
        scanNumber = i * 90;
        break;
    }
}

// scan and save images allowing up to a minute for each scan
await foreach (var image in controller.Scan(options))
{
    image.Save($"scanPage_{scanNumber}.png"); // save scan as png
    Console.WriteLine($"Saved scanPage{scanNumber}.png"); // confirmation output
    scanNumber++; // increment scan number in case multiple scans are done
}

Console.WriteLine("Completed scanning process.");
