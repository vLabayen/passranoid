import sys
import readline
from os import popen, listdir
from os.path import isdir
from printer import cprepare

class InputManager:
    def __init__(self, config):
        self.config = config

        self.commands = sorted([
            'create', 'import', 'passgen', 'clear', 'help',
            'use', 'select', 'insert', 'remove', 'list',
            'changedbpass', 'changedbkey', 'export', 'version',
            'exit'
        ])
        self.commands_usage = {
            'create' : 'usage : create [dbname]',
            'import' : 'usage : import [dbfile]',
            'passgen' : 'usage : passgen [length] [alphabet]',
            'use' : 'usage : use [dbname]',
            'select' : 'usage : select [service]',
            'insert' : 'usage : insert [service] [user]',
            'remove' : 'usage : remove [index]',
            'export' : 'usage : export [dbfile]'
        }
        self.commands_args_help = {
            'import' : {1 : 'ls'},
            'use' : {1 : 'existing_dbs'},
            'export' : {1 : 'ls'}
        }

        self.cache = []
        self.autocompletion = True
        self.buffer = None
        self.prompt = None
        readline.set_completer(self.autocomplete)
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(self.displaymatches)

    def autocomplete(self, text, state):
        if state == 0: # on first trigger, build possible matches
            if not self.autocompletion : return None
            else :
                if self.buffer is not None:
                    self.cache = ['-', '.'] #Arbitrary matches to inside command
                    return self.cache[0]
                else:
                    buf = readline.get_line_buffer()
                    if any([buf.startswith(c) for c in self.commands]) :
                        self.cache = ['-', '_'] #Arbitrary matches to outside command but already writed
                        return self.cache[0]
                    else: options = self.commands

            if text: self.cache = [o for o in options if o.startswith(text)]
            else : self.cache = options

        try : return self.cache[state]
        except IndexError : return None

    def displaymatches(self, substitution, matches, longest_match_length):
        line_buffer = readline.get_line_buffer()
        columns = int(popen('stty size', 'r').read().split()[1])
        print()

        if matches == ['-', '_'] : self.command_help("passranoid>> {}", line_buffer, columns, line_buffer)
        elif matches == ['-', '.']: self.command_help(self.prompt, '{}{}'.format(self.buffer, line_buffer), columns, line_buffer)
        else :
            template = '{}{}{}'.format('{:<', int(longest_match_length + 3), '}')
            matches = [template.format(m) for m in matches]
            longest_print_len = max(map(len, matches))
            self.print_matches(matches, longest_print_len, columns)

            print("passranoid>> {}".format(line_buffer), end="")
            sys.stdout.flush()

    def print_matches(self, matches, longest_print_len, columns):
        display = [""]
        display_len = 0
        for match in matches:
            if (display_len + longest_print_len) >= columns:
                display.append("")
                display_len = 0
            display[-1] += match
            display_len += longest_print_len

        for line in display : print(line)

    def command_help(self, prompt, line_buffer, columns, real_buffer):
        buf = line_buffer.split(' ')
        if len(buf) == 1:
            #Print command usage if the command require args and not args are already specified
            try : h = self.commands_usage[buf[0]]
            except : pass
            else : print(h)
        else:
            #Print help based on which is the actual argument
            arg_index = len(buf[1:])
            try : h = self.commands_args_help[buf[0]][arg_index] #Get help type
            except : pass
            else :
                if h ==  'existing_dbs':
                    searching_pattern = buf[arg_index]
                    options = list(self.config.keys())
                elif h == 'ls' :
                    paths = buf[arg_index].split('/')
                    search_dir = '/'.join(p for p in paths[:-1] if p != '')
                    searching_pattern = paths[-1]
                    if buf[arg_index].startswith('/') : search_dir = '/{}'.format(search_dir)

                    if search_dir == '' : options = listdir()
                    else : options = listdir(search_dir)
                    options += ['.', '..']

                #Prepare print template
                if len(options) == 0: longest_match_length = 0
                else : longest_match_length = max(map(len, options))
                match_print_len = int(longest_match_length + 3)
                template = '{}{}{}'.format('{:<', match_print_len, '}')

                #Filter options based on what is already writed and if it start with . in ls mode
                options = [o for o in options if o.startswith(searching_pattern)]
                if h == 'ls' and not searching_pattern.startswith('.'): options = [o for o in options if not o.startswith('.')]

                #If just one option, perform autocompletion.
                if len(options) == 1:
                    readline.insert_text(options[0][len(searching_pattern):])

                    #Add / if ls mode and a dir is autocompleted
                    if h == 'ls':
                        full_path = '{}/{}'.format(search_dir, options[0]) if search_dir != '' else options[0]
                        if isdir(full_path): readline.insert_text('/')

                #For more than one option, print options
                elif len(options) > 0:
                    #If all the options have a common start, autocomplete that common part
                    common_start = options[0][0:([min([elem==seq[0] for elem in seq]+[True]) for seq in zip(*options)] + [False]).index(False)]
                    if common_start != '': readline.insert_text(common_start[len(searching_pattern):])

                    #Format the options to equal lenght. If ls mode, give blue color to dirs
                    if h == 'ls':
                        path_template = '{}/{}'.format(search_dir, '{}') if search_dir != '' else '{}'
                        options = [(cprepare(template.format('{}/'.format(o)), color = 'lblue') if isdir(path_template.format(o)) else template.format(o)) for o in options]
                    else : options = [template.format(o) for o in options]

                    self.print_matches(options, match_print_len, columns)

        print(prompt.format(real_buffer), end="")
        sys.stdout.flush()

    def input(self, prompt, history = True):
        t = input(prompt)
        if not history and t != '': readline.remove_history_item(readline.get_current_history_length() - 1)
        return t

    def is_something_writed(self): return (readline.get_line_buffer() != '')

    def set_buffer(self, buffer, prompt):
        self.autocompletion = True
        self.buffer = buffer
        self.prompt = '{}{}'.format(prompt, '{}')

    def clear_buffer(self, autocompletion = False):
        self.autocompletion = autocompletion
        self.buffer = None
        self.prompt = None
