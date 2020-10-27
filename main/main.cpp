#include "pch.h"


/*int wmain(int argc, wchar_t* argv[])
{
	_putenv_s("PYTHONPATH", "python");
	return Py_Main(argc, argv);
}*/

extern "C" int WINAPI wWinMain(
	_In_ HINSTANCE hInstance,
	_In_opt_ HINSTANCE hPrevInstance,
	_In_ LPTSTR lpCmdLine,
	_In_ int nShowCmd
)
{
	if (__argc > 1)
	{
		return Py_Main(__argc, __wargv);
	}

	_putenv_s("PYTHONPATH", "python");
	Py_Initialize();

	/*PyObject * pModule = PyImport_ImportModule("main");

	if (pModule == NULL) {
		if (PyErr_Occurred())
			PyErr_Print();
	}*/

	if (Py_IsInitialized())
	{
		FILE* fp;
		fopen_s(&fp, "python/main.py", "rb");

		if (fp)
		{
			PyRun_AnyFileEx(fp, "main", 1);
		}

		if (Py_FinalizeEx() < 0) {
			exit(120);
		}
	}

	return 0;
}