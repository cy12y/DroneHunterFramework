# core/module.py
import importlib
import os

def get_all_modules():
    modules = []
    module_dir = os.path.join(os.path.dirname(__file__), '..', 'modules')
    i = 0
    for filename in os.listdir(module_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Module'
            module = importlib.import_module(f'modules.{module_name}')
            #print(f"Attempting to load module class: {class_name} from {module_name}")
            module_class = getattr(module, class_name)
            modules.append(module_class())
            print(f"{i}: module {module_name} loaded")
            i +=1
    return modules
