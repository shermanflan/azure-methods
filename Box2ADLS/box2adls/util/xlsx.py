from os.path import split

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from box2adls.exceptions import XlsxFormatError
from box2adls.logging import root_logger as logger


def transform_daily(prev_month, prev_label, curr_month, curr_label,
                    next_month, next_label, source):
    """
    Transform daily Excel file.

    :param prev_month: Name of previous month
    :param prev_label: New name of previous month tab
    :param curr_month: Name of current month
    :param curr_label: New name of current month tab
    :param next_month: Name of next month
    :param next_label: New name of next month tab
    :param source: path to file (xlsx)
    :return: None
    """
    logger.info(f'Renaming worksheet tabs for {split(source)[1]}')

    wb = load_workbook(filename=source)

    if prev_month in wb:
        ws = wb[prev_month]
        ws.title = prev_label
    else:
        raise XlsxFormatError(f"Invalid file format: {split(source)[1]}")

    if curr_month in wb:
        ws = wb[curr_month]
        ws.title = curr_label
    else:
        raise XlsxFormatError(f"Invalid file format: {split(source)[1]}")

    if next_month in wb:
        ws = wb[next_month]
        ws.title = next_label
    else:
        raise XlsxFormatError(f"Invalid file format: {split(source)[1]}")

    wb.save(filename=source)


def transform_weekly(tab_name, tab_rename, source):
    """
    Transform weekly Excel file.

    :param tab_name: name of hidden tab
    :param tab_rename: new tab name
    :param source: path to file (xlsx)
    :return: None
    """
    logger.info(f'Enabling worksheet for {split(source)[1]}')

    wb = load_workbook(filename=source)

    if tab_name in wb:
        ws = wb[tab_name]
        ws.title = tab_rename
        ws.sheet_state = Worksheet.SHEETSTATE_VISIBLE
    else:
        raise XlsxFormatError(f"Invalid file format: {split(source)[1]}")

    wb.save(filename=source)
