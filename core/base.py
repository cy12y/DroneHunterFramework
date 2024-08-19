# core/base.py

class BaseModule:
    def __init__(self, name, description, category):
        self.name = name
        self.description = description
        self.category = category
        self.options = {}

    def set_option(self, key, value):
        if key in self.options:
            self.options[key]["value"] = value
        else:
            print(f"Option {key} does not exist.")

    def show_options(self):
        print("Options:")
        for key, val in self.options.items():
            print(f"{key}: {val['value']} ({'Required' if val['required'] else 'Optional'}) - {val['description']}")

    def run(self):
        raise NotImplementedError("You must implement the run method in your module.")
