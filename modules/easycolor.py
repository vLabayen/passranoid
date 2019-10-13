def ec_internal_print(template, config, print_args):
    '''uses print and termcolor to get a colored output in the terminal
    Input :
        template : A string with the format of the output
            example : 'Your name is {} and your age {}'
        config : A config arr of dict objects to replace the {} for the colored texts
            the array must have as much objects as {} in the templace
            each dict can have the following properties:
            {"text":yourdata, "color":yourcolor, "bg_color":yourbg }
                - text is a required property, str() will be applied, so can be any basic datatype
                - color and bg_color does not need to be present
                    both properties have the same valid values:
                        'red','green','yellow','blue','maggenta','cyan','white'
    Output : (printed to the terminal)
        The result of replacing each {} in the template by a colored text
        The replacing are made in the element order of the config arr.
        The text property of the element is colored with the color and bg_color properties if present
    See help(termcolor.colored) for more info
    '''
    import termcolor

    #Get a full config object (optional properties)
    full_config = []
    for c in config:
        obj = {}

        #text is a required argument
        try : obj['text'] = c['text']
        except KeyError: raise ValueError("could't find property text in {}".format(c))

        #color and bg_color are optional arguments
        try :
            if c['color'] != None: obj['color'] = c['color']
            else : obj['color'] = None
        except KeyError: obj['color'] = None

        try :
            if c['bg_color'] != None: obj['bg_color'] = 'on_{}'.format(c['bg_color'])
            else : obj['bg_color'] = None
        except KeyError:
            obj['bg_color'] = None

        full_config.append(obj)

    #Get the colored version of the input texts
    ctext = [termcolor.colored(
        text = str(x['text']),
        color = x['color'],
        on_color = x['bg_color']
    ) for x in full_config]

    #Format and print
    if print_args == None:
        print(template.format(*[t for t in ctext]))
    else :
        print(template.format(*[t for t in ctext]), **print_args)

def ec_config(texts, colors = None, bg_colors = None):
    '''creates a config object for ec_print based on arrays
    Input :
        texts is an array of the texts we want to print
        colors could be a string or an array. if not supplied, the text will not be colored
            if string : all the texts will be asociated to this color
            if array : the text element in the n'th position will take the n'th color
                if colors is shorter than the texts arr the lasts elements of texts will be uncolored (same as color None)
        bg_colors behaves like colors: could be str or arr, with same behaviours
    Output
        A config arr of dict for the ec_print function
        see help(ec_internal_print) to see the detailed structure of this arr
    '''
    config = []
    for text_index in range(len(texts)):
        c_obj = {'text' : texts[text_index]}

        if colors != None:
            if isinstance(colors, list):
                try : c_obj['color'] = colors[text_index]
                except IndexError: c_obj['color'] = None
            else : c_obj['color'] = colors

        if bg_colors != None:
            if isinstance(bg_colors, list):
                try : c_obj['bg_color'] = bg_colors[text_index]
                except IndexError: c_obj['bg_color'] = None
            else:
                c_obj['bg_color'] = bg_colors

        config.append(c_obj)

    return config

def ecprint(texts, c = None, bg_c = None, template = None, **kargs):
    '''wrapper for termcolor.colored & print & str.format
    texts : text or array of texts to introduce as arguments in str.format() after termcolor processing
    c : color or array of colors to process the text. see examples
    bg_c : backgroud color of the text. same behaviour as c
    template : str template to use the format with. a default one is generated if not provided
        something like template.format(*texts) should work to make this function works too
    accepts keyword arguments to the print function

    Examples:
    ecprint('hello')
    ecprint('hello', template='{} blablabla')
    ecprint('hello', template='{} blablabla', c='blue')
    ecprint('hello', template='{} blablabla', c='blue', bg_c='red')
    ecprint('\n'*1, end = '') #print('\n', end='')
    ecprint(['hello', True, 90, 12.234])
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}')
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c='yellow')
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c=['yellow'])
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c=['yellow', None, 'blue', 'red'])
    ecprint('\n'*1, end = ''})
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c='red', bg_c='magenta')
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c='red', bg_c=['magenta'])
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c='red', bg_c=['magenta', None, 'white', 'green'])
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c=['yellow','cyan', 'red', 'green'], bg_c='magenta')
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c=['yellow','cyan', 'red', 'green'], bg_c=['magenta', 'red'])
    ecprint(['hello', True, 90, 12.234], template='{} --- {} --- {} --- {}', c=['yellow','cyan', 'red', 'green'], bg_c=['magenta', None, 'blue', 'white'])
    '''

    if isinstance(texts, list):
        if template == None:
            template = ' - '.join(['{}' for x in texts])
    else:
        texts = [texts]
        if template == None:
            template = '{}'

    conf = ec_config(texts, colors = c, bg_colors = bg_c)
    ec_internal_print(template, conf, kargs)
