from InquirerPy import inquirer
from InquirerPy.utils import get_style
from colorama import Fore, Style
from time import sleep
from random import uniform, choice, randint
import sys
import json
import base64
import os
import asyncio
import prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.patch_stdout import patch_stdout

def typewriter(string):
    for x in string:
        print(x, end='')
        sys.stdout.flush()
        if not (x == "\\" or x == "["):
            sleep(uniform(0.02, 0.12))
    print()

def clear_screen():
    if not os.environ.get("PYCHARM_HOSTED"):
        os.system('cls' if os.name == 'nt' else 'clear')

def json_encode(data):
    return base64.b64encode(json.dumps(data).encode()).decode()

def json_decode(encoded):
    json_text = base64.b64decode(encoded).decode("utf-8")
    return json.loads(json_text)

style = get_style(
    {
        "question": "bold",
        "questionmark": "#ec3750",
        "pointer": "#ec3750",
        "answer": "#ec3750",
    },
    style_override=False,
)

states = ("hunger",)
alert = ""

def mainGame(name):
    clear_screen()
    try:
        with open("gamestate.txt", "r") as f:
            save = json_decode(f.read())
        with open("backpack.txt", "r") as f:
            inv = json_decode(f.read())
    
    except Exception:
        save = {}
        inv = {}
    
    state = save.get("state", {"happiness": 100, "hunger": 0, "age": 1})
    backpack = {"coins": 69, "cookie": 1}
    backpack.update(inv)
    ui = {"shopping": False}

    async def hunger_loop():
        while True:
            await asyncio.sleep(randint(10, 60))
            if ui["shopping"]:
                continue
            state["hunger"] = min(100, state["hunger"] + 1)

    toolbarStyle = prompt_toolkit.styles.Style.from_dict({
        "bottom-toolbar": "#000000 bg:#ffffff",
    })

    async def life_cycle(name):
        while True:
            await asyncio.sleep(randint(10,40))
            if ui["shopping"]:
                continue
            currentState = choice(states)
            global alert
            if currentState == "hunger" and (int(state['hunger']) > 45):
                alert = f"<b>{name}</b> is hungry"
                if int(state['hunger']) > 80:
                    alert = f"<b>{name}</b> is very hungry"


    def toolbar():
        return HTML(
            f"Happiness [<b>{state['happiness']:>3}</b>]   "
            f"Hunger [<b>{state['hunger']:>3}</b>]   "
            f"Age [<b>{state['age']:>3}</b>]   "
            f"⌾ Coins [<b>{backpack['coins']}</b>]\n"
            f"{alert}"
        )

    async def input_loop():
        session = PromptSession(
            "> ",
            bottom_toolbar=toolbar,
            style=toolbarStyle,
            refresh_interval=0.5,
        )
        
        while True:
            try:
                cmd = (await session.prompt_async()).strip().lower()
            except (EOFError, KeyboardInterrupt):
                return

            cmd_parts = cmd.split()
        
            if not cmd_parts:
                continue

            main_cmd = cmd_parts[0]

            if main_cmd == "quit":
                return
            
            elif main_cmd == "help":
                print(Style.BRIGHT + Fore.CYAN + "Help Menu" + Style.RESET_ALL)
                print("feed" + Style.DIM + f" - Feeds {name}" + Style.RESET_ALL)
                print("shop" + Style.DIM + " - Go shopping" + Style.RESET_ALL)
                print("quit" + Style.DIM + " - Save and go back" + Style.RESET_ALL)

            elif main_cmd == "feed":
                if len(cmd_parts) > 1:
                    item = " ".join(cmd_parts[1:])
                    if backpack.get(item, 0) > 0:
                        backpack[item] -= 1
                        state["hunger"] = max(0, state["hunger"] - 5)
                        print(f"You fed {name} a {item}")
                        global alert
                        alert = "-5 Hunger!"
                    else:
                        print(f"{Style.BRIGHT}{item}{Style.RESET_ALL} was not found in your inventory")
                else:
                    print(f"You should specify what to feed {name}")
                    print("Try 'feed cookie'")

            elif main_cmd == "shop":
                defaulter = "Flavourtown" if state["hunger"] > 45 else "Toys R Us"

                ui["shopping"] = True
                try:
                    shopChoice = await inquirer.select(
                        message="Grow an Orpheus",
                        choices=["Toys R Us", "Flavourtown", "Back"],
                        default=defaulter,
                        qmark="$",
                        amark="",
                        style=style,
                    ).execute_async()
                finally:
                    ui["shopping"] = False

                if shopChoice == "Flavourtown":
                    flavourtown = await inquirer.select(
                        message="Flavourtown",
                        choices=["Cookie | 1⌾", "Back"],
                        default=defaulter,
                        qmark="$",
                        amark="",
                        style=style,
                    ).execute_async()

                    if flavourtown == "Cookie":
                        backpack["coins"] -= 1
                        backpack["cookie"] += 1
                elif shopChoice == "Toys R Us":
                    print("toys")
                elif shopChoice == "Back":
                    continue

            else:
                print("Unknown action. Type 'help' for help!")

    async def main_loop():
        bg = [
            asyncio.create_task(hunger_loop()),
            asyncio.create_task(life_cycle(name))
        ]
        try:
            with patch_stdout(raw=True):
                await input_loop()
        finally:
            for t in bg:
                t.cancel()
            await asyncio.gather(*bg, return_exceptions=True)

    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass

    save["state"] = state
    with open("gamestate.txt", "w") as f:
        f.write(json_encode(save))

    with open("backpack.txt", "w") as f:
        f.write(json_encode(backpack))

def new_game():
    clear_screen()
    pronoun = choice(["him", "her"])

    print(f"Huh? An {Style.BRIGHT}egg!{Style.RESET_ALL}")
    sleep(0.5)
    print("...It's hatching...")
    sleep(1)
    print(f"Woah! {Style.BRIGHT}Baby Orpheus{Style.RESET_ALL} :>")
    sleep(1)

    while True:
        name = input(f"What would you like to name {pronoun}?\n").strip().capitalize()
        if name:
            break
        print(Fore.RED + "Please enter a valid name." + Style.RESET_ALL)

    print("Loading...")
    with open("gamestate.txt", "w") as f:
        f.write(json_encode({"name": name}))
    with open("backpack.txt", "w") as f:
        f.write(json_encode({"coins": 100}))
    print("Done!")
    clear_screen()
    typewriter(f"Welcome to the world, {Style.BRIGHT}{Fore.CYAN}{name}{Style.RESET_ALL}!")
    sleep(0.5)
    mainGame(name)

def main():
    while True:
        clear_screen()
        if os.path.exists("gamestate.txt"):
            try:
                with open("gamestate.txt", "r") as f:
                    json = json_decode(f.read())
                saveName = json["name"]
            except:
                print("Save not found or corrupted")
                saveName = ""

            mainChoices = ["New Game", f"Continue - {saveName}", "Quit"]
            defaulter = f"Continue - {saveName}"
        else:
            mainChoices = ["New Game", "Quit"]
            defaulter = "New Game"

        menuChoice = inquirer.select(
            message="Grow an Orpheus",
            choices=mainChoices,
            default=defaulter,
            qmark="",
            amark="",
            style=style,
        ).execute()

        if menuChoice == "New Game":
            if os.path.exists("gamestate.txt"):
                print(Fore.RED + Style.BRIGHT + "This will delete your previous save!" + Style.RESET_ALL)
                restartChoice = inquirer.select(
                    message="Are you sure you want to do this?",
                    choices=["Yes", "No"],
                    qmark="⚠",
                    amark="",
                    style=style,
                    default="No",
                ).execute()

                if restartChoice == "No":
                    clear_screen()
                    continue

            new_game()
            break

        elif menuChoice == f"Continue - {saveName}":
            with open("gamestate.txt", "r") as f:
                json = json_decode(f.read())
            name = json["name"]
            mainGame(name)

        elif menuChoice == "Quit":
            print("Goodbye!")
            sleep(0.2)
            return

if __name__ == "__main__":
    main()