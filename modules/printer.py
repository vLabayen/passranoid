#https://misc.flogisoft.com/bash/tip_colors_and_formatting

MODE = {
    'normal' : '{}',
    'bold' : '\033[1m{}',
    'dim' : '\033[2m{}',
    'underlined' : '\033[4m{}',
    'blink' : '\033[5m{}',
    'inverted' : '\033[7m{}',
    'hidden' : '\033[8m{}'
}
COLOR = {
    'default' : '\033[39m{}',           'black' : '\033[30m{}',                 'white' : '\033[97m{}',
    'red' : '\033[31m{}',               'lred' : '\033[38;5;196m{}',            'dred' : '\033[38;5;88m{}',
    'green' : '\033[32m{}',             'lgreen' : '\033[38;5;82m{}',           'dgreen' : '\033[38;5;22m{}',
    'yellow' : '\033[38;5;184m{}',      'lyellow' : '\033[38;5;226m{}',         'dyellow' : '\033[38;5;142m{}',
    'blue' : '\033[34m{}',              'lblue' : '\033[94m{}',                 'dblue' : '\033[38;5;17m{}',
    'magenta' : '\033[38;5;132m{}',     'lmagenta' : '\033[95m{}',              'dmagenta' : '\033[35m{}',
    'cyan' : '\033[38;5;43m{}',         'lcyan' : '\033[38;5;14m{}',            'dcyan' : '\033[36m{}',
    'orange' : '\033[38;5;214m{}',      'lorange' : '\033[38;5;202m{}',         'dorange' : '\033[38;5;172m{}',
    'gray' : '\033[38;5;245m{}',        'lgray' : '\033[38;5;240m{}',           'dgray' : '\033[38;5;250m{}'
}

def cprepare(text, color='default', mode='normal'):
    return '{}\033[0m'.format(COLOR[color].format(MODE[mode].format(text)))

def cprint(text, color = 'default', mode='normal', **kargs):
    print(cprepare(text, color, mode), **kargs)

def ctable(header, data,
    header_color = 'default', header_mode = 'normal',
    rows_color = 'default', rows_mode = 'normal',
    table_color = 'default', table_mode = 'normal',
    side_spacing = 1, horizontal_separator = '-', vertical_separator = '|'):

    header = [str(h) for h in header]
    data = [[str(d) for d in row] for row in data]

    row_items_count = len(data[0])
    vertical_separator_len = len(vertical_separator)
    horizontal_separator_len = len(horizontal_separator)
    longest_match_length = max([max(map(len, header))] + [max(map(len, row)) for row in data])
    row_len = (2 * vertical_separator_len) + (vertical_separator_len * (row_items_count - 1)) + (row_items_count * (longest_match_length + (2 * side_spacing)))

    item_template = '{}{}{}{}{}'.format(side_spacing * ' ', '{:<', longest_match_length, '}', side_spacing * ' ')
    external_horizontal_line = cprepare(horizontal_separator * row_len, color = table_color, mode = table_mode)
    internal_horizontal_line = cprepare('{}{}{}'.format(vertical_separator, vertical_separator.join([horizontal_separator * (longest_match_length + (2 * side_spacing))] * row_items_count), vertical_separator) , color = table_color, mode = table_mode)
    header_line_template = '{}{}{}'.format(
        cprepare(vertical_separator, color = table_color, mode = table_mode),
        cprepare(vertical_separator.join([item_template] * row_items_count), color = header_color, mode = header_mode),
        cprepare(vertical_separator, color = table_color, mode = table_mode)
    )
    data_line_template = '{}{}{}'.format(
        cprepare(vertical_separator, color = table_color, mode = table_mode),
        cprepare(vertical_separator.join([item_template] * row_items_count), color = rows_color, mode = rows_mode),
        cprepare(vertical_separator, color = table_color, mode = table_mode)
    )

    print(external_horizontal_line)
    print(header_line_template.format(*header))
    print(internal_horizontal_line)
    for row in data: print(data_line_template.format(*row))
    print(external_horizontal_line)
