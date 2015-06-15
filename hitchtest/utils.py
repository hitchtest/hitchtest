from IPython.terminal.embed import InteractiveShellEmbed
import IPython
import inspect

def to_underscore_style(text):
    text = text.lower().replace(" ", "_").replace("-", "_")
    return ''.join(x for x in text if x.isalpha() or x.isdigit() or x == "_")

def ipython(message=None, frame=None):
    """Launch into customized IPython with greedy autocompletion and no prompt to exit."""
    config = IPython.Config({
        'InteractiveShell': {'confirm_exit': False, },
        'IPCompleter': {'greedy': True, }
    })
    InteractiveShellEmbed.instance(config=config)(message, local_ns=frame.f_locals, global_ns=frame.f_globals)

def ipython_embed(message=None, functions_above=0):
    frame = inspect.stack()[functions_above + 1][0]
    ipython(message, frame)
