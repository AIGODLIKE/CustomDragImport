import ctypes
from ctypes.wintypes import *


GMEM_MOVABLE = 2
INT_P = ctypes.POINTER(ctypes.c_int)

CF_UNICODETEXT = 13
CF_HDROP = 15
CF_BITMAP = 2   # hbitmap
CF_DIB = 8   # DIB and BITMAP are interconvertable as from windows clipboard
CF_DIBV5 = 17

# bitmap compression types
BI_RGB = 0
BI_RLE8 = 1
BI_RLE4 = 2
BI_BITFIELDS = 3
BI_JPEG = 4
BI_PNG = 5
BI_ALPHABITFIELDS = 6

format_dict = {
    1: 'CF_TEXT',
    2: 'CF_BITMAP',
    3: 'CF_METAFILEPICT',
    4: 'CF_SYLK',
    5: 'CF_DIF',
    6: 'CF_TIFF',
    7: 'CF_OEMTEXT',
    8: 'CF_DIB',
    9: 'CF_PALETTE',
    10: 'CF_PENDATA',
    11: 'CF_RIFF',
    12: 'CF_WAVE',
    13: 'CF_UNICODETEXT',
    14: 'CF_ENHMETAFILE',
    15: 'CF_HDROP',
    16: 'CF_LOCALE',
    17: 'CF_DIBV5',
}

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1  # structure field byte alignment
    _fields_ = [
        ('bfType', WORD),  # file type ("BM")
        ('bfSize', DWORD),  # file size in bytes
        ('bfReserved1', WORD),  # must be zero
        ('bfReserved2', WORD),  # must be zero
        ('bfOffBits', DWORD),  # byte offset to the pixel array
    ]
sizeof_BITMAPFILEHEADER = ctypes.sizeof(BITMAPFILEHEADER)

class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1  # structure field byte alignment
    _fields_ = [
        ('biSize', DWORD),
        ('biWidth', LONG),
        ('biHeight', LONG),
        ('biPLanes', WORD),
        ('biBitCount', WORD),
        ('biCompression', DWORD),
        ('biSizeImage', DWORD),
        ('biXPelsPerMeter', LONG),
        ('biYPelsPerMeter', LONG),
        ('biClrUsed', DWORD),
        ('biClrImportant', DWORD)
    ]
sizeof_BITMAPINFOHEADER = ctypes.sizeof(BITMAPINFOHEADER)

class BITMAPV4HEADER(ctypes.Structure):
    _pack_ = 1 # structure field byte alignment
    _fields_ = [
        ('bV4Size', DWORD),
        ('bV4Width', LONG),
        ('bV4Height', LONG),
        ('bV4PLanes', WORD),
        ('bV4BitCount', WORD),
        ('bV4Compression', DWORD),
        ('bV4SizeImage', DWORD),
        ('bV4XPelsPerMeter', LONG),
        ('bV4YPelsPerMeter', LONG),
        ('bV4ClrUsed', DWORD),
        ('bV4ClrImportant', DWORD),
        ('bV4RedMask', DWORD),
        ('bV4GreenMask', DWORD),
        ('bV4BlueMask', DWORD),
        ('bV4AlphaMask', DWORD),
        ('bV4CSTypes', DWORD),
        ('bV4RedEndpointX', LONG),
        ('bV4RedEndpointY', LONG),
        ('bV4RedEndpointZ', LONG),
        ('bV4GreenEndpointX', LONG),
        ('bV4GreenEndpointY', LONG),
        ('bV4GreenEndpointZ', LONG),
        ('bV4BlueEndpointX', LONG),
        ('bV4BlueEndpointY', LONG),
        ('bV4BlueEndpointZ', LONG),
        ('bV4GammaRed', DWORD),
        ('bV4GammaGreen', DWORD),
        ('bV4GammaBlue', DWORD)
    ]
sizeof_BITMAPV4HEADER = ctypes.sizeof(BITMAPV4HEADER)

class BITMAPV5HEADER(ctypes.Structure):
    _pack_ = 1 # structure field byte alignment
    _fields_ = [
        ('bV5Size', DWORD),
        ('bV5Width', LONG),
        ('bV5Height', LONG),
        ('bV5PLanes', WORD),
        ('bV5BitCount', WORD),
        ('bV5Compression', DWORD),
        ('bV5SizeImage', DWORD),
        ('bV5XPelsPerMeter', LONG),
        ('bV5YPelsPerMeter', LONG),
        ('bV5ClrUsed', DWORD),
        ('bV5ClrImportant', DWORD),
        ('bV5RedMask', DWORD),
        ('bV5GreenMask', DWORD),
        ('bV5BlueMask', DWORD),
        ('bV5AlphaMask', DWORD),
        ('bV5CSTypes', DWORD),
        ('bV5RedEndpointX', LONG),
        ('bV5RedEndpointY', LONG),
        ('bV5RedEndpointZ', LONG),
        ('bV5GreenEndpointX', LONG),
        ('bV5GreenEndpointY', LONG),
        ('bV5GreenEndpointZ', LONG),
        ('bV5BlueEndpointX', LONG),
        ('bV5BlueEndpointY', LONG),
        ('bV5BlueEndpointZ', LONG),
        ('bV5GammaRed', DWORD),
        ('bV5GammaGreen', DWORD),
        ('bV5GammaBlue', DWORD),
        ('bV5Intent', DWORD),
        ('bV5ProfileData', DWORD),
        ('bV5ProfileSize', DWORD),
        ('bV5Reserved', DWORD)
    ]
sizeof_BITMAPV5HEADER = ctypes.sizeof(BITMAPV5HEADER)


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

user32.OpenClipboard.argtypes = HWND,
user32.OpenClipboard.restype = BOOL
user32.GetClipboardData.argtypes = UINT,
user32.GetClipboardData.restype = HANDLE
user32.SetClipboardData.argtypes = UINT, HANDLE
user32.SetClipboardData.restype = HANDLE
user32.CloseClipboard.argtypes = None
user32.CloseClipboard.restype = BOOL
user32.IsClipboardFormatAvailable.argtypes = UINT,
user32.IsClipboardFormatAvailable.restype = BOOL
user32.CountClipboardFormats.argtypes = None
user32.CountClipboardFormats.restype = UINT
user32.EnumClipboardFormats.argtypes = UINT,
user32.EnumClipboardFormats.restype = UINT
user32.GetClipboardFormatNameA.argtypes = UINT, LPSTR, UINT
user32.GetClipboardFormatNameA.restype = UINT
user32.RegisterClipboardFormatA.argtypes = LPCSTR,
user32.RegisterClipboardFormatA.restype = UINT
user32.RegisterClipboardFormatW.argtypes = LPCWSTR,
user32.RegisterClipboardFormatW.restype = UINT
user32.RegisterClipboardFormatW.argtypes = LPCWSTR,
user32.RegisterClipboardFormatW.restype = UINT
user32.EmptyClipboard.argtypes = None
user32.EmptyClipboard.restype = BOOL

kernel32.GlobalAlloc.argtypes = UINT, ctypes.c_size_t
kernel32.GlobalAlloc.restype = HGLOBAL
kernel32.GlobalSize.argtypes = HGLOBAL,
kernel32.GlobalSize.restype = UINT
kernel32.GlobalLock.argtypes = HGLOBAL,
kernel32.GlobalLock.restype = LPVOID
kernel32.GlobalUnlock.argtypes = HGLOBAL,
kernel32.GlobalUnlock.restype = BOOL

shell32.DragQueryFile.argtypes = HANDLE, UINT, ctypes.c_void_p, UINT
shell32.DragQueryFile.restype = UINT