// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include <windows.h>
#include <stdio.h>
#include "keyhook.h"


#pragma data_seg("shared")
HHOOK g_hHook = NULL;
DWORD g_ownerThreadID = NULL;
bool g_onKeyUp = false;
#pragma data_seg()
#pragma comment(linker,"/SECTION:shared,RWS")


// extern "C"  __declspec(dllexport)
LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam)
{
	if (nCode == HC_ACTION)
	{
		bool isUp = (lParam & 0x80000000) != 0;
		if (g_onKeyUp ? isUp: !isUp)
		{
			PostThreadMessage(g_ownerThreadID, WM_HOOK_KEY, wParam, lParam);
		}
	}
	return CallNextHookEx(g_hHook, nCode, wParam, lParam);
}

LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    KBDLLHOOKSTRUCT* key = (KBDLLHOOKSTRUCT*)lParam;
    if (HC_ACTION == nCode)
    {
        if (g_onKeyUp ? (wParam == WM_KEYUP || wParam == WM_SYSKEYUP): (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN))
        {
            WPARAM t_wParam = key->vkCode; // 按键码
            LPARAM t_lParam = 0; // 兼容WH_KEYBOARD

            if (key->flags & LLKHF_ALTDOWN) // ALT键
            {
                t_lParam |= 0x20000000;
            }
            PostThreadMessage(g_ownerThreadID, WM_HOOK_KEY, t_wParam, t_lParam);
        }
    }
    return CallNextHookEx(g_hHook, nCode, wParam, lParam); //回调
}


HHOOK SetHook(DWORD ownerThreadID, DWORD targetThreadID, bool onKeyUp)
{
	HMODULE mod = GetModuleHandle(L"keyhook.dll");   // 获取当前DLL模块句柄
    if (targetThreadID != NULL)
    {
	    g_hHook = SetWindowsHookEx(WH_KEYBOARD, KeyboardProc, mod, targetThreadID);
    }
    else
    {
        g_hHook = SetWindowsHookEx(WH_KEYBOARD_LL, LowLevelKeyboardProc, mod, targetThreadID);
    }
	g_ownerThreadID = ownerThreadID;
	g_onKeyUp = onKeyUp;
	return g_hHook;
}

void UnsetHook()
{
	if (g_hHook)
	{
		::UnhookWindowsHookEx(g_hHook);
		g_hHook = NULL;
	}
}


BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

