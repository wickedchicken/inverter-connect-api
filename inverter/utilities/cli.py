from __future__ import annotations

import sys

from bx_py_utils.iteration import chunk_iterable
from rich import print  # noqa
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.panel import Panel
from rich.table import Table

from inverter.data_types import ModbusResponse
from inverter.exceptions import ModbusNoData, ModbusNoHexData


def convert_address_option(raw_address: str, debug: bool = True) -> int:
    """
    >>> convert_address_option(raw_address='0x123', debug=True)
    Address: 0x123
    291
    >>> convert_address_option(raw_address='456', debug=True)
    Address: 0x1c8
    456
    """
    if 'x' in raw_address:
        base = 16
    else:
        base = 10
    address = int(raw_address, base=base)
    if debug:
        print('Address:', hex(address))

    return address


def print_hex_table(address, data_hex, title):
    table = Table(title=title)
    table.add_column('Counter\n', justify='right')
    table.add_column('Address\n(hex)', justify='center', style='cyan')
    table.add_column('Address\n(dec)', justify='right', style='cyan')
    table.add_column('[green]Value\n(hex)', justify='center', style='green')
    table.add_column('Value\n(dec)', justify='right', style='magenta')

    for offset, values in enumerate(chunk_iterable(iterable=data_hex, chunk_size=2)):
        hex_value = ''.join(values)
        table.add_row(
            str(offset + 1),  # Counter
            hex(address + offset),  # Address (hex)
            str(address + offset),  # Address (dec)
            hex_value,  # Hex value
            f'{int(hex_value, 16):>2}',  # Decimal
        )

    console = Console()
    console.print(table)


def print_register(inv_sock, start_register, length):
    try:
        response: ModbusResponse = inv_sock.read(start_register=start_register, length=length)
    except ModbusNoHexData as err:
        print(f'[yellow]Non hex response: [magenta]{err.data!r}')
    except ModbusNoData:
        print('[yellow]no data')
    else:
        print(response)
        print(f'\nResult (in hex): [cyan]{response.data_hex}\n')

        print_hex_table(
            address=start_register,
            data_hex=response.data_hex,
            title=f'[green][bold]{length} value(s) from {hex(start_register)}',
        )


def exit_with_human_error(
    *,
    hint: str,
    title='Hint',
    exit_code=-1,
    print_traceback: BaseException | None = None,
    HintHighlighterClass=ReprHighlighter,
    hint_border_style='bright_yellow',
    hint_padding=(2, 5),
):
    """
    TODO: Move to a shared package!
    """
    console = Console()
    console.print('\n')

    if print_traceback is not None:
        assert isinstance(print_traceback, BaseException), f'Not a exception: {print_traceback!r}'
        console.print_exception(show_locals=True)

    console.print()

    if HintHighlighterClass is not None:
        highlighter = HintHighlighterClass()
        hint = highlighter(text=hint)

    console.print(
        Panel(
            hint,
            title=f'[bright][green]{title}',
            border_style=hint_border_style,
            expand=False,
            padding=hint_padding,
        )
    )
    console.print()

    sys.exit(exit_code)
