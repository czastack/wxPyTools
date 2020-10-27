#pragma once

#define WM_HOOK_KEY WM_USER + 0x10

extern "C" {
	__declspec(dllexport) HHOOK SetHook(DWORD ownerThreadID, DWORD targetThreadID, bool onKeyUp=false);

	__declspec(dllexport) void UnsetHook();
}