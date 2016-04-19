# my_module.py =========================================================
''' This is the documentation
      for my example module'''

'''Naming convenctions:
    Function names must be lowercase separated by underscores '_'
    An underscore '_' at the beginning of a functuin name means the function is
    intended to be private BUT Python do NOT enforce this rule:
    you can break the code if you want! '''

# Variables defined here are available for ALL the functions in the module
# When module is imported, these variable can be accessed with:
#    module_name.variable_name
module_variable = 1

# Constants are named in uppercase
MODULE_CONSTANT = 1

def my_function(name):
    ''' This is the documentation for "my_function"'''
    # Variables defined inside functions are local
    (first, family) = name                       # Arguments bundled in a Tuple
    return _my_private_function(first, family)

def _my_private_function(first_name, second_name):
    ''' This is the documentation for "_my_private_function"'''
    full_name = first_name + ' [' + second_name.upper() + ']'
    return full_name
    
if __name__ == '__main__':
    ''' This is a Unit Test: use "run my_module" from Python interpreter'''
    print('This is the testing code:')
    print(my_function(('Johnn', 'Doe')))
