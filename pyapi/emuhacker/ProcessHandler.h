#pragma once
#include <windows.h>
#include <string>
#include <vector>

typedef size_t addr_t;
typedef wchar_t* STR;
typedef const wchar_t* CSTR;


class ProcessHandler
{
protected:
	HANDLE		m_process;
	DWORD       m_thread_id;
	HWND        m_hwnd;
	static bool m_is64os;
	bool        m_is32process; // target is 32bit process
	bool        m_raw_addr;

public:
	ProcessHandler();
	virtual ~ProcessHandler();

	virtual bool attach() { return false; }
	virtual addr_t address_map(addr_t addr) {
		return addr;
	};

	/*
	 * close the handle
	 */
	void close();

	/**
	 * find the first process whose main window has the specified class and window name,
	 * the handle will be automatically closed, unless it is detached
	 */
	bool attach_window(CSTR className, CSTR windowName);

	/*
	 * attach the process whose main window is the specified window
	 * the handle will be automatically closed, unless it is detached
	 */
	bool attach_handle(HWND hWnd);

	/*
	 * return value is TRUE, if this object has attached to a valid process handle
	 */
	bool isValid();

	bool is32Process();
	auto getProcess() { return m_process; }
	DWORD getProcessId() { return ::GetProcessId(m_process); }
	auto getHWnd() { return m_hwnd; }

	int getPtrSize() { return m_is32process ? 4 : 8; }

	bool raw_read(addr_t addr, LPVOID buffer, size_t size);
	bool raw_write(addr_t addr, LPCVOID buffer, size_t size);

	bool read(addr_t addr, LPVOID buffer, size_t size);
	bool write(addr_t addr, LPCVOID buffer, size_t size);

	bool add(addr_t addr, int value)
	{
		DWORD origin = read<DWORD>(addr);
		origin += value;
		return write(addr, origin);
	}

	size_t read_uint(addr_t addr, size_t size)
	{
		size_t data = 0;
		read(addr, &data, size);
		return data;
	}

	bool write_uint(addr_t addr, size_t data, size_t size)
	{
		return write(addr, &data, size);
	}

	INT64 read_int(addr_t addr, size_t size)
	{
		INT64 data = (INT64)read_uint(addr, size);
		switch (size)
		{
		case 1:
			data = (char)data;
			break;
		case 2:
			data = (short)data;
			break;
		case 4:
			data = (int)data;
			break;
		default:
			break;
		}
		return data;
	}

	bool write_int(addr_t addr, long long data, size_t size)
	{
		return write_uint(addr, data & ((1ull << (size << 3ull)) - 1ull), size);
	}

	/**
	 * read data to array
	 */
	template<size_t size, typename TYPE>
	bool read(addr_t addr, TYPE(&arr)[size]) {
		return read(addr, arr, size * sizeof(TYPE));
	}

	/**
	 * write data in array
	 */
	template<size_t size, typename TYPE>
	bool write(addr_t addr, TYPE(&arr)[size]) {
		return write(addr, arr, size * sizeof(TYPE));
	}

	/**
	 * read data to buffer
	 */
	template<typename TYPE>
	bool read(addr_t addr, TYPE &buff) {
		return read(addr, &buff, sizeof(TYPE));
	}

	/**
	 * write data in buff
	 */
	template<typename ValueType>
	bool write(addr_t addr, const ValueType &buff) {
		return write(addr, &buff, sizeof(ValueType));
	}

	/**
	 * read data of type
	 */
	template<typename ValueType=BYTE>
	ValueType read(addr_t addr) {
		ValueType data;
		read(addr, data);
		return data;
	}

	addr_t read_addr(addr_t addr)
	{
#ifdef _WIN64
		if (m_is32process)
		{
			addr &= 0xFFFFFFFF;
		}
#endif

		if (!read(addr, &addr,
#ifdef _WIN64
			m_is32process ? sizeof(DWORD) :
#endif
			sizeof(addr)))
		{
			return 0;
		}

		return addr;
	}

	bool ptr_read(addr_t addr, DWORD offset, size_t size, LPVOID buffer) {
		addr = read_addr(addr);
		if (addr)
			return read(addr + offset, buffer, size);
		return false;
	}
	bool ptr_write(addr_t addr, DWORD offset, size_t size, LPCVOID buffer) {
		addr = read_addr(addr);
		if (addr)
			return write(addr + offset, buffer, size);
		return false;
	}

	template<typename ListType>
	addr_t read_last_addr(addr_t addr, const ListType &offsets) {
		for (auto const offset : offsets) {
			addr = read_addr(addr);
			if (!addr)
				return 0;

			addr += offset;
		}
		return addr;
	}

	/**
	 * read data from pointers
	 */
	template<typename ListType>
	bool ptrs_read(addr_t addr, const ListType &offsets, size_t size, LPVOID buffer) {
		addr = read_last_addr(addr, offsets);
		return addr && read(addr, buffer, size);
	}

	/**
	 * write data by pointers
	 */
	template<typename ListType>
	bool ptrs_write(addr_t addr, const ListType &offsets, size_t size, LPCVOID buffer) {
		addr = read_last_addr(addr, offsets);
		return addr && write(addr, buffer, size);
	}

	// bool bring_target_top();

	addr_t getProcessBaseAddress();

	addr_t getModuleHandle(LPCTSTR name);

	addr_t alloc_memory(size_t start, size_t size, DWORD allocationType = MEM_COMMIT | MEM_RESERVE, DWORD protect = PAGE_READWRITE);
	void free_memory(addr_t addr);

	addr_t alloc_data(LPCVOID buf, size_t size, size_t start=0);
	addr_t write_function(LPCVOID buf, size_t size, size_t start=0);

	DWORD remote_call(addr_t addr, LONG_PTR arg);
	class ProcAddressHelper* getProcAddressHelper(addr_t module);

	addr_t find_bytes(BYTE * data, addr_t data_size, addr_t start, addr_t end, int ordinal=1, bool fuzzy=false);
};


class ProcAddressHelper
{
private:
	ProcessHandler * m_handler;
	LPVOID m_pides;
	addr_t m_module;
public:
	ProcAddressHelper(ProcessHandler *handler, LPVOID pides, addr_t module);
	~ProcAddressHelper();
	std::vector<size_t> getProcAddress(const std::vector<std::string> &name_list);
};