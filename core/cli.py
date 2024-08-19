# core/cli.py

# Remove the unnecessary import
# from core.base import CommandLine
from core.module import get_all_modules

class DroneHunterCLI:
    def __init__(self):
        self.modules = get_all_modules()
        self.selected_module = None
        self.commands = {
            "search": [1, "query"],
            "use": [1, "module_name"],
            "show": [1, "options"],
            "set": [2, "option", "value"],
            "exploit": [0],
            "help": [0],
            "exit": [0],
        }

    def split_command(self, command):
        return command.strip().lower().split()

    def execute_command(self, command_array):
        if not command_array:
            print("No command entered.")
            return

        action = command_array[0]
        if action not in self.commands:
            print(f"Unknown command: {action}")
            return

        expected_args = self.commands[action][0]
        if len(command_array) - 1 != expected_args:
            print(f"Incorrect number of arguments for '{action}'. Expected {expected_args}.")
            return

        if action == "search":
            query = command_array[1]
            self.search_modules(query)
        elif action == "use":
            module_name = command_array[1]
            self.use_module(module_name)
        elif action == "show" and command_array[1] == "options":
            self.show_options()
        elif action == "set":
            option = command_array[1]
            value = command_array[2]
            self.set_option(option, value)
        elif action == "exploit":
            self.exploit()
        elif action == "help":
            self.show_help()
        elif action == "exit":
            self.exit_cli()

    def search_modules(self, query):
        matches = [mod for mod in self.modules if query in mod.name.lower()]
        print("Matching Modules")
        print("================")
        if matches:
            for i, mod in enumerate(matches):
                print(f"{i}  {mod.name}  {mod.description}")
        else:
            print("No matching modules found.")

    def use_module(self, module_name):
        if module_name.isdigit():
            index = int(module_name)
            if 0 <= index < len(self.modules):
                self.selected_module = self.modules[index]
                print(f"Using module: {self.selected_module.name}")
            else:
                print("Invalid module index.")
        else:
            self.selected_module = next((mod for mod in self.modules if mod.name == module_name), None)
            if self.selected_module:
                print(f"Using module: {self.selected_module.name}")
            else:
                print("Module not found.")

    def show_options(self):
        if self.selected_module:
            self.selected_module.show_options()
        else:
            print("No module selected.")

    def set_option(self, option, value):
        if self.selected_module:
            self.selected_module.set_option(option, value)
            print(f"Set {option} to {value}")
        else:
            print("No module selected.")

    def exploit(self):
        if self.selected_module:
            self.selected_module.run()
        else:
            print("No module selected.")

    def show_help(self):
        print("Commands: search <query>, use <index|name>, show options, set <option> <value>, exploit, help, exit")

    def exit_cli(self):
        print("Exiting DroneHunter...")
        exit(1)

    def start_cli(self):
        # Commented out the CommandLine banner printing as it's not implemented
        # CommandLine.print_banner()
        if not self.modules:
            print("No modules found.")
            return
        while True:
            command = input("DroneHunter > ")
            command_array = self.split_command(command)
            self.execute_command(command_array)

# This block allows the CLI to start if the module is run directly
if __name__ == "__main__":
    cli = DroneHunterCLI()
    cli.start_cli()
