#include <stdlib.h>

static void xamarin_initialize_dotnet ()
{
}

extern "C" void xamarin_initialize_dotnet();
extern "C" void xamarin_create_classes_Microsoft_macOS();

static void xamarin_invoke_registration_methods ()
{
	xamarin_initialize_dotnet();
	xamarin_create_classes_Microsoft_macOS();
}

#include "xamarin/xamarin.h"


void xamarin_register_modules_impl ()
{

}

void xamarin_register_assemblies_impl ()
{
	GCHandle exception_gchandle = INVALID_GCHANDLE;

}

static const char *xamarin_runtime_libraries_array[] = {
	"libSystem.Globalization.Native",
	"libSystem.IO.Compression.Native",
	"libSystem.Native",
	"libSystem.Net.Security.Native",
	"libSystem.Security.Cryptography.Native.Apple",
	"libSystem.Security.Cryptography.Native.OpenSsl",
	"libclrgc",
	"libclrjit",
	"libcoreclr",
	"libhostfxr",
	"libhostpolicy",
	"libmscordaccore",
	"libmscordbi",
	NULL
};
void xamarin_setup_impl ()
{
	xamarin_invoke_registration_methods ();
	xamarin_libmono_native_link_mode = XamarinNativeLinkModeDynamicLibrary;
	xamarin_runtime_libraries = xamarin_runtime_libraries_array;
	xamarin_gc_pump = FALSE;
	xamarin_init_mono_debug = TRUE;
	xamarin_executable_name = "scanner-controller.dll";
	xamarin_log_level = 0;
	xamarin_arch_name = "arm64";
	xamarin_marshal_objectivec_exception_mode = MarshalObjectiveCExceptionModeThrowManagedException;
	xamarin_debug_mode = TRUE;
	setenv ("MONO_GC_PARAMS", "major=marksweep", 1);
	xamarin_supports_dynamic_registration = TRUE;
	xamarin_runtime_configuration_name = "runtimeconfig.bin";
}

int main (int argc, char **argv)
{
	NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	int rv = xamarin_main (argc, argv, XamarinLaunchModeApp);
	[pool drain];
	return rv;
}

void xamarin_initialize_callbacks () __attribute__ ((constructor));
void xamarin_initialize_callbacks ()
{
	xamarin_setup = xamarin_setup_impl;
	xamarin_register_assemblies = xamarin_register_assemblies_impl;
	xamarin_register_modules = xamarin_register_modules_impl;
}
