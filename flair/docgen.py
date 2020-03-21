import types

from flair.hook import input, process, window, storage
import inspect

output = ''

# for module in input, process, window, storage:
#     output += module.__name__ + '\n<dl>\n'
#     print(list(getattr(module, t) for t in dir(module)))
#     moduleattrs = sorted(dir(module), key=lambda t: inspect.findsource(getattr(module, t))[1] if isinstance(getattr(module, t), types.FunctionType) else float('inf'))
#     for function in [getattr(module, a) for a in moduleattrs if isinstance(getattr(module, a), types.FunctionType) and getattr(module, a).__module__ == module.__name__]:
#         output += '<dt>' + function.__name__ + str(inspect.signature(function)) + '</dt>\n'
#         output += '<dd>' + str(inspect.getdoc(function)) + '</dd>\n\n'
# output += '</dl>\n\n\n'
# print(output)

for module in input, process, window, storage:
    output += '#### ' + module.__name__.split('.')[-1].capitalize() + '\n'
    path_to_module = module.__name__.replace('.', '/')
    output += f'Source: [{path_to_module}]({path_to_module})'
    moduleattrs = sorted(dir(module), key=lambda t: inspect.findsource(getattr(module, t))[1] if isinstance(getattr(module, t), types.FunctionType) else float('inf'))
    for function in [getattr(module, a) for a in moduleattrs if isinstance(getattr(module, a), types.FunctionType) and getattr(module, a).__module__ == module.__name__]:
        if function.__name__.startswith('_'):
            continue
        output += '##### `' + function.__name__ + str(inspect.signature(function)) + '`\n'
        output += str(inspect.getdoc(function)) + '\n\n'
output += '\n\n\n'
print(output)
