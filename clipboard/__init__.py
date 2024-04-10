"""
Clipette

Python clipboard utility that works natively on python with its inbuilt
modules to exchange data with the windows clipboard.
Is designed particularly to work properly with different image formats.
Supports only the Windows clipboard through win32 API.

Usage (setting):
    import clipette
    if clipette.open_clipboard():
        clipette.empty_cliboard()
        clipette.set_UNICODETEXT("<some text>")
        clipette.close_clipboard()

Usage (getting):
    import clipette
    if clipette.open_clipboard():
        clipette.get_PNG("<filepath to save into>", "filename")
        clipette.close_clipboard()

"""

import ctypes
from os.path import join as path_join
import sys
import locale
from contextlib import contextmanager

try:
    from . import clipboard_utils as utils
except ImportError:
    import clipboard_utils as utils


class ClipetteWin32ClipboardError(Exception):
    """
    Raised when the clipboard is inaccessible or clipette is unable to
    exchange given data with the clipboard.
    """


class ClipetteWin32MemoryError(Exception):
    pass


# the following functions to raise error safely after closing clipboard
def _raise_clipboard_error(error_msg: str) -> None:
    close_clipboard()
    raise ClipetteWin32ClipboardError(error_msg)


def _raise_memory_error(error_msg: str) -> None:
    close_clipboard()
    raise ClipetteWin32MemoryError(error_msg)


def _global_alloc(flags: int, size: int) -> int:
    h_mem = utils.kernel32.GlobalAlloc(flags, size)
    if (h_mem == None):
        _raise_memory_error("Unable to allocate memory.")
    else:
        return h_mem


def _global_lock(h_mem: int) -> int:
    lp_mem = utils.kernel32.GlobalLock(h_mem)
    if (lp_mem == None):
        _raise_memory_error("Unable to lock global memory object.")
    else:
        return lp_mem


def _global_unlock(h_mem: int) -> int:
    utils.kernel32.GlobalUnlock(h_mem)


def _get_clipboard_data(format: int) -> int:
    h_mem = utils.user32.GetClipboardData(format)
    if (h_mem == None):
        _raise_clipboard_error("Unable to access clipboard data.")
    else:
        return h_mem


def _set_clipboard_data(format: int, h_mem: int) -> int:
    h_data = utils.user32.SetClipboardData(format, h_mem)
    if (h_data == None):
        _raise_clipboard_error("Unable to set clipboard data.")
    else:
        return h_data


def open_clipboard() -> int:
    """
    Opens clipboard. Must be called before any action in performed.

    :return: 0 if function fails, 1 otherwise.
    :rtype: int
    """
    return utils.user32.OpenClipboard(None)


def close_clipboard() -> int:
    """
    Closes clipboard. Must be called after all actions are performed.

    :return: 0 if function fails, 1 otherwise.
    :rtype: int
    """
    return utils.user32.CloseClipboard()


@contextmanager
def clipboard():
    """
    Context manager to open and close clipboard automatically.

    :return: if function fails, 1 otherwise.
    :rtype: int
    """
    res = open_clipboard()
    yield res
    if res: close_clipboard()


def empty_clipboard() -> int:
    """
    Empties clipboard. Should be called before any setter actions.

    :return: 0 if function fails, 1 otherwise.
    """
    return utils.user32.EmptyClipboard()


def get_UNICODETEXT() -> str:
    """
    Gets text from clipboard as a string.

    :return: text grabbed from clipboard.
    :rtype: str
    """

    # user32.OpenClipboard(0)
    h_mem = _get_clipboard_data(utils.CF_UNICODETEXT)
    lp_mem = _global_lock(h_mem)
    text = ctypes.wstring_at(lp_mem)
    _global_unlock(h_mem)
    # user32.CloseClipboard()

    return text


def set_UNICODETEXT(text: str) -> bool:
    """
    Sets text to clipboard in CF_UNICODETEXT format.

    :param text: text to set to clipboard.
    :type text: str
    :return: True if function succeeds.
    :rtype: bool
    """

    data = text.encode('utf-16le')
    size = len(data) + 2

    h_mem = _global_alloc(utils.GMEM_MOVABLE, size)
    lp_mem = _global_lock(h_mem)
    ctypes.memmove(lp_mem, data, size)
    _global_unlock(h_mem)

    # user32.OpenClipboard(0)
    # user32.EmptyClipboard()
    _set_clipboard_data(utils.CF_UNICODETEXT, h_mem)
    # user32.CloseClipboard()
    return True


def get_FILEPATHS() -> list[str]:
    """
    Gets list of filepaths from clipboard.

    :return: list of filepaths.
    :rtype: list[str]
    """

    filepaths = []
    # user32.OpenClipboard(0)
    h_mem = _get_clipboard_data(utils.CF_HDROP)
    file_count = utils.shell32.DragQueryFile(h_mem, -1, None, 0)
    for index in range(file_count):
        buf = ctypes.c_buffer(260)
        utils.shell32.DragQueryFile(h_mem, index, buf, ctypes.sizeof(buf))
        filepaths.append(buf.value.decode(locale.getpreferredencoding()))
    # user32.CloseClipboard()

    return filepaths


def get_DIB(filepath: str = '', filename: str = 'bitmap') -> str:
    """
    Gets image from clipboard as a bitmap and saves to *filepath* as *filename.bmp*.

    :param filepath: filepath to save image into.
    :type filepath: str
    :param filename: filename of the image.
    :type filename: str
    :return: full filepath of the saved image.
    :rtype: str
    """

    # user32.OpenClipboard(0)
    if not is_format_available(utils.CF_DIB):
        _raise_clipboard_error("clipboard image not available in 'CF_DIB' format")

    h_mem = _get_clipboard_data(utils.CF_DIB)
    lp_mem = _global_lock(h_mem)
    size = utils.kernel32.GlobalSize(lp_mem)
    data = bytes((ctypes.c_char * size).from_address(lp_mem))

    bm_ih = utils.BITMAPINFOHEADER()
    header_size = utils.sizeof_BITMAPINFOHEADER
    ctypes.memmove(ctypes.pointer(bm_ih), data, header_size)

    compression = bm_ih.biCompression
    if compression not in (utils.BI_BITFIELDS, utils.BI_RGB):
        _raise_clipboard_error(f'unsupported compression type {format(compression)}')

    bm_fh = utils.BITMAPFILEHEADER()
    ctypes.memset(ctypes.pointer(bm_fh), 0, utils.sizeof_BITMAPFILEHEADER)
    bm_fh.bfType = ord('B') | (ord('M') << 8)
    bm_fh.bfSize = utils.sizeof_BITMAPFILEHEADER + len(str(data))
    sizeof_COLORTABLE = 0
    bm_fh.bfOffBits = utils.sizeof_BITMAPFILEHEADER + header_size + sizeof_COLORTABLE

    img_path = path_join(filepath, filename + '.bmp')
    with open(img_path, 'wb') as bmp_file:
        bmp_file.write(bm_fh)
        bmp_file.write(data)

    _global_unlock(h_mem)
    # user32.CloseClipboard()
    return img_path


def get_DIBV5(filepath: str = '', filename: str = 'bitmapV5') -> str:
    """
    Gets image from clipboard as a bitmapV5 and saves to *filepath* as *filename.bmp*.

    :param str filepath: filepath to save image into.
    :type filepath: str
    :param filename: filename of the image.
    :type filename: str
    :return: full filepath of the saved image.
    :rtype: str
    """

    # user32.OpenClipboard(0)
    if not is_format_available(utils.CF_DIBV5):
        _raise_clipboard_error("clipboard image not available in 'CF_DIBV5' format")

    h_mem = _get_clipboard_data(utils.CF_DIBV5)
    lp_mem = _global_lock(h_mem)
    size = utils.kernel32.GlobalSize(lp_mem)
    data = bytes((ctypes.c_char * size).from_address(lp_mem))

    bm_ih = utils.BITMAPV5HEADER()
    header_size = utils.sizeof_BITMAPV5HEADER
    ctypes.memmove(ctypes.pointer(bm_ih), data, header_size)

    if bm_ih.bV5Compression == utils.BI_RGB:
        # convert BI_RGB to BI_BITFIELDS so as to properly support an alpha channel
        # everything other than the usage of bitmasks is same compared to BI_BITFIELDS so we manually add that part and put bV5Compression to BI_BITFIELDS
        # info on these header structures -> https://docs.microsoft.com/en-us/windows/win32/gdi/bitmap-header-types
        # and -> https://en.wikipedia.org/wiki/BMP_file_format

        bi_compression = bytes([3, 0, 0, 0])
        bi_bitmasks = bytes([0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 0, 0, 0, 0, 255])
        data = data[:16] + bi_compression + data[20:40] + bi_bitmasks + data[56:]

    elif bm_ih.bV5Compression == utils.BI_BITFIELDS:
        # we still need to add bitmask (bV5AlphaMask) for softwares to recognize the alpha channel
        data = data[:52] + bytes([0, 0, 0, 255]) + data[56:]

    else:
        _raise_clipboard_error(f'unsupported compression type {format(bm_ih.bV5Compression)}')

    bm_fh = utils.BITMAPFILEHEADER()
    ctypes.memset(ctypes.pointer(bm_fh), 0, utils.sizeof_BITMAPFILEHEADER)
    bm_fh.bfType = ord('B') | (ord('M') << 8)
    bm_fh.bfSize = utils.sizeof_BITMAPFILEHEADER + len(str(data))
    sizeof_COLORTABLE = 0
    bm_fh.bfOffBits = utils.sizeof_BITMAPFILEHEADER + header_size + sizeof_COLORTABLE

    img_path = path_join(filepath, filename + '.bmp')
    with open(img_path, 'wb') as bmp_file:
        bmp_file.write(bm_fh)
        bmp_file.write(data)

    _global_unlock(h_mem)
    # user32.CloseClipboard()
    return img_path


def get_PNG(filepath: str = '', filename: str = 'PNG') -> str:
    """
    Gets image in ``PNG`` or ``image/png`` format from clipboard and saves to *filepath* as *filename.png*.

    :param str filepath: filepath to save image into.
    :type filepath: str
    :param filename: filename of the image.
    :type filename: str
    :return: full filepath of the saved image.
    :rtype: str
    """

    # user32.OpenClipboard(0)
    png_format = 0
    PNG = utils.user32.RegisterClipboardFormatW(ctypes.c_wchar_p('PNG'))
    image_png = utils.user32.RegisterClipboardFormatW(ctypes.c_wchar_p('image/png'))
    if utils.user32.IsClipboardFormatAvailable(PNG):
        png_format = PNG
    elif utils.user32.IsClipboardFormatAvailable(image_png):
        png_format = image_png
    else:
        _raise_clipboard_error("clipboard image not available in 'PNG' or 'image/png' format")

    h_mem = _get_clipboard_data(png_format)
    lp_mem = _global_lock(h_mem)
    size = utils.kernel32.GlobalSize(lp_mem)
    data = bytes((ctypes.c_char * size).from_address(lp_mem))
    _global_unlock(h_mem)
    # user32.CloseClipboard()

    img_path = path_join(filepath, filename + '.png')
    with open(img_path, 'wb') as png_file:
        png_file.write(data)

    return img_path


def set_DIB(src_bmp: str) -> bool:
    """
    Sets given bitmap image to clipboard in ``CF_DIB`` or ``CF_DIBV5`` format according to the image.

    :param src_bmp: full filepath of source image.
    :type src_bmp: str
    :return: True if function succeeds.
    :rtype: bool
    """

    with open(src_bmp, 'rb') as img:
        data = img.read()
    output = data[14:]
    size = len(output)
    print(list(bytearray(output)[:200]))

    h_mem = _global_alloc(utils.GMEM_MOVABLE, size)
    lp_mem = _global_lock(h_mem)
    ctypes.memmove(ctypes.cast(lp_mem, utils.INT_P), ctypes.cast(output, utils.INT_P), size)
    _global_unlock(h_mem)

    if output[0] in [56, 108, 124]:
        # img contains DIBV5 or DIBV4 or DIBV3 Header
        fmt = utils.CF_DIBV5
    else:
        fmt = utils.CF_DIB

    # user32.OpenClipboard(0)
    # user32.EmptyClipboard()
    _set_clipboard_data(fmt, lp_mem)
    # user32.CloseClipboard()
    return 1


def set_PNG(src_png: str) -> bool:
    """
    Sets source PNG image to clipboard in ``PNG`` format.

    :param src_png: full filepath of source image.
    :type src_png: str
    :return: True if function succeeds.
    :rtype: bool
    """

    with open(src_png, 'rb') as img:
        data = img.read()
    size = len(data)

    h_mem = _global_alloc(utils.GMEM_MOVABLE, size)
    lp_mem = _global_lock(h_mem)
    ctypes.memmove(lp_mem, data, size)
    _global_unlock(h_mem)

    # user32.OpenClipboard(0)
    # user32.EmptyClipboard()
    PNG = utils.user32.RegisterClipboardFormatW(ctypes.c_wchar_p('PNG'))
    _set_clipboard_data(PNG, lp_mem)
    # user32.CloseClipboard()
    return True


def is_format_available(format_id: int) -> bool:
    """
    Checks whether specified format is currently available on the clipboard.

    :param format_id: id of format to check for.
    :type format_id: int
    :return: True if specified format is available, False otherwise.
    :rtype: bool
    """

    # user32.OpenClipboard(0)
    is_format = utils.user32.IsClipboardFormatAvailable(format_id)
    # user32.CloseClipboard()
    return bool(is_format)


def get_available_formats(buffer_size: int = 32) -> dict[int, str]:
    """
    Gets a dict of all the currently available formats on the clipboard.

    :param buffer_size: (optional) buffer size to store name of each format in.
    :type buffer_size: int
    :return: a dict {format_id : format_name} of all available formats.
    :rtype: dict[int, str]
    """

    available_formats = dict()
    # user32.OpenClipboard(0)
    fmt = 0
    for i in range(utils.user32.CountClipboardFormats()):
        # must put previous fmt (starting from 0) in EnumClipboardFormats() to get the next one
        fmt = utils.user32.EnumClipboardFormats(fmt)
        name_buf = ctypes.create_string_buffer(buffer_size)
        name_len = utils.user32.GetClipboardFormatNameA(fmt, name_buf, buffer_size)
        fmt_name = name_buf.value.decode()

        # standard formats do not return any name, so we set one from out dictionary
        if fmt_name == '' and fmt in utils.format_dict.keys():
            fmt_name = utils.format_dict[fmt]
        available_formats.update({fmt: fmt_name})

    # user32.CloseClipboard()
    return available_formats


def get_image(filepath: str = '', filename: str = 'image') -> str:
    """
    Gets image from clipboard in a format according to a priority list (``PNG`` > ``DIBV5`` > ``DIB``).

    :param filepath: filepath to save image into.
    :type filepath: str
    :param filename: filename of the image.
    :type filename: str
    :return: full filepath of the saved image.
    :rtype: str
    """

    # user32.OpenClipboard(0)
    PNG = utils.user32.RegisterClipboardFormatW(ctypes.c_wchar_p('PNG'))
    image_png = utils.user32.RegisterClipboardFormatW(ctypes.c_wchar_p('image/png'))

    if utils.user32.IsClipboardFormatAvailable(PNG) or utils.user32.IsClipboardFormatAvailable(image_png):
        return get_PNG(filepath, filename)
    elif utils.user32.IsClipboardFormatAvailable(utils.CF_DIBV5):
        return get_DIBV5(filepath, filename)
    elif utils.user32.IsClipboardFormatAvailable(utils.CF_DIB):
        return get_DIB(filepath, filename)
    else:
        _raise_clipboard_error('image on clipboard not available in any supported format')


def set_image(src_img: str) -> bool:
    """
    (NOT FULLY IMPLEMENTED) Sets source image to clipboard in multiple formats (``PNG``, ``DIB``).

    :param src_img: full filepath of source image.
    :type src_img: str
    :return: True if function succeeds.
    :rtype: bool
    """

    # this is more complicated... gotta interconvert images
    # looking into ways to get this done with ctypes as well - NO IM DONE

    # temporary solution
    img_extn = src_img[(len(src_img) - 3):].lower()
    if img_extn == 'bmp':
        set_DIB(src_img)
    elif img_extn == 'png':
        set_PNG(src_img)
    else:
        _raise_clipboard_error('Unsupported image format')

    return True


if __name__ == '__main__':
    pass

