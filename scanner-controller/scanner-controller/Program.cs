// See https://aka.ms/new-console-template for more information

using NAPS2.Images;
using NAPS2.Images.Gdi;
using NAPS2.Pdf;
using NAPS2.Scan;

// Set up the scanning context
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
    Dpi = 300
};

// Scan and save images
int i = 1;
await foreach (var image in controller.Scan(options))
{
    image.Save($"page{i++}.jpg");
}

// Scan and save as PDF
var images = new List<ProcessedImage>();
await foreach (var image in controller.Scan(options))
{
    images.Add(image);
}
var pdfExporter = new PdfExporter(scanningContext);
await pdfExporter.Export("document.pdf", images);


Console.WriteLine("Hello, World!");
