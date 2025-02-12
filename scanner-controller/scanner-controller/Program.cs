// See https://aka.ms/new-console-template for more information

using NAPS2.Images;
using NAPS2.Images.Gdi;
using NAPS2.Scan;

// Set up the scanning context
// TODO: Add checks for what platform is running it
// windows check
using var scanningContext = new ScanningContext(new GdiImageContext());
var controller = new ScanController(scanningContext);

// Query for available scanning devices
var devices = await controller.GetDeviceList();

// Set scanning options
var options = new ScanOptions
{
    Device = devices.First(),
    PaperSource = PaperSource.Feeder,
    PageSize = PageSize.A4,
    Dpi = 4800
};

// Scan and save images
// send out .png format images
int i = 1;
await foreach (var image in controller.Scan(options))
{
    image.Save($"page{i++}.png");
}


Console.WriteLine("Hello, World!");
