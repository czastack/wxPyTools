-- 调试KERNELBASE.WriteProcessMemory (64位)
local WriteProcessMemory = getAddress('KERNELBASE.WriteProcessMemory')
function readHex(addr, size)
    local data = readBytes(addr, size, true)
    local hexdata = {}
    for k, v in ipairs(data) do
        hexdata[k] = string.format('%02X', v)
    end
    return string.format("'%s'", table.concat(hexdata, ' '))
end
function debugger_onBreakpoint()
    -- LPVOID lpBaseAddress: RDX,
    -- LPVOID lpBuffer: ECX,
    -- DWORD nSize: R9,
    if RIP ~= WriteProcessMemory + 0x13 then
        return 0
    end
    local replace = readHex(R8, R9)
    local result = string.format('WriteProcessMemory(address=0x%08X, replace=%s, size=%d)', RDX, replace, R9)
    print(result)
    return 1
end

debug_setBreakpoint(WriteProcessMemory + 0x13)

-- 调试KERNELBASE.WriteProcessMemory (32位)
local WriteProcessMemory = getAddress('KERNELBASE.WriteProcessMemory')
function readHex(addr, size)
    local data = readBytes(addr, size, true)
    local hexdata = {}
    for k, v in ipairs(data) do
        hexdata[k] = string.format('%02X', v)
    end
    return string.format("'%s'", table.concat(hexdata, ' '))
end
function debugger_onBreakpoint()
    -- LPVOID lpBaseAddress: ESP + 8,
    -- LPVOID lpBuffer: ESP + C,
    -- DWORD nSize: ESP + 10,
    if EIP ~= WriteProcessMemory then
       return 0
    end
    local lpBaseAddress = readInteger(ESP + 8)
    local lpBuffer = readInteger(ESP + 0xC)
    local nSize = readInteger(ESP + 0x10)
    local replace = readHex(lpBuffer, nSize)
    local result = string.format('WriteProcessMemory(address=0x%08X, replace=%s, size=%d)', lpBaseAddress, replace, nSize)
    print(result)
    return 1
end

debug_setBreakpoint(WriteProcessMemory)


function findBytes(data)
    local result = AOBScan(data, '+X-C-W')
    for i=0, result.Count - 1 do
        if string.find(result[i], '7FF') == 1 then
            print(result[i], data)
        end
    end
end

print(string.format("base=0x%08X", getAddress('re2.exe')))


-- 写入文件
print(writeRegionToFile('F:/Temp/1.txt', 0x0087C9E6, 1024 * 20))
