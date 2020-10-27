#include "pch.h"
#ifdef _WIN32
#include "auto.h"
#undef _


/**
 * input_list = [(vk, scan, codetype, keyup)]
 */
void sendKey(py::list &input_list, DWORD interval=0)
{
	int vk, scan, codetype;
	bool keyup;

	size_t length = py::len(input_list);
	INPUT *inputs = new INPUT[length];

	for (size_t i = 0; i < length; ++i)
	{
		const py::tuple &item = input_list[i].cast<py::tuple>();
		scan = item[1].cast<int>();
		codetype = item[2].cast<int>();
		keyup = item[3].cast<bool>();

		if (keyup)
		{
			codetype |= KEYEVENTF_KEYUP;
		}
		if (codetype == KEYEVENTF_UNICODE)
		{
			vk = 0;
		}
		else {
			vk = item[0].cast<int>();
		}

		inputs[i].type = INPUT_KEYBOARD;
		KEYBDINPUT &keybd = inputs[i].ki;
		keybd.wVk = vk;
		keybd.wScan = scan;
		keybd.dwFlags = codetype;

	}

	if (!interval)
	{
		SendInput((UINT)length, inputs, sizeof(INPUT));
	}
	else
	{
		// 带有时间间隔
		for (size_t i = 0; i < length; ++i)
		{
			SendInput(1, inputs + i, sizeof(INPUT));
			Sleep(interval);
		}
	}
	delete inputs;
}


inline py::tuple KeyInputArg(int keycode, int scan, int codetype, bool keyup)
{
	py::tuple ret = py::tuple(4);
	ret[0] = keycode;
	ret[1] = scan;
	ret[2] = codetype;
	ret[3] = keyup;
	return ret;
}


py::tuple VKey(int keycode, bool keyup=false)
{
	return KeyInputArg(keycode, 0, 0, keyup);
}


/**
 * 使用UNICODE时，基本和VKey等效
 */
py::tuple ScanKey(int keycode, int codetype=KEYEVENTF_UNICODE, bool keyup=false)
{
	return KeyInputArg(0, keycode, codetype, keyup);
}

py::list CombKey(int mod, int keycode)
{
	py::list ret;
	if (mod & MOD_SHIFT)
		ret.append(VKey(VK_SHIFT));
	if (mod & MOD_CONTROL)
		ret.append(VKey(VK_CONTROL));
	if (mod & MOD_ALT)
		ret.append(VKey(VK_MENU));

	ret.append(VKey(keycode));
	ret.append(VKey(keycode, true));

	if (mod & MOD_SHIFT)
		ret.append(VKey(VK_SHIFT, true));
	if (mod & MOD_CONTROL)
		ret.append(VKey(VK_CONTROL, true));
	if (mod & MOD_ALT)
		ret.append(VKey(VK_MENU, true));

	return ret;
}

py::list TextKeys(wchar_t *text)
{
	py::list ret;

	while (*text)
	{
		ret.append(ScanKey(*text));
		ret.append(ScanKey(*text, KEYEVENTF_UNICODE, true));
		++text;
	}
	return ret;
}

void init_auto(py::module & m)
{
	using namespace py::literals;
	py::module auto_ = m.def_submodule("auto");

	py::arg keycode("keycode");
	py::arg_v keyup("keyup", false);

	auto_.def("sendKey", sendKey, "input_list"_a, "interval"_a=0)
		.def("VKey", VKey, keycode, keyup)
		.def("ScanKey", ScanKey, keycode, "codetype"_a=KEYEVENTF_UNICODE, keyup)
		.def("CombKey", CombKey, "mod"_a, keycode)
		.def("TextKeys", TextKeys, "text"_a);

	PyObject_SetAttrString(auto_.ptr(), "UNICODE", PyLong_FromLong(KEYEVENTF_UNICODE));
	PyObject_SetAttrString(auto_.ptr(), "SCANCODE", PyLong_FromLong(KEYEVENTF_SCANCODE));
}

#endif