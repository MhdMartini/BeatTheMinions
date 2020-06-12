import sys
import time
from pygame import mixer


BANNER_1 = '''
.************ Welcome to Beat the Minions ****************. '''
BANNER_2 = '''
 * If you hate Minions, this is the right place for you! *
 * Enjoy crushing those Minions, but be careful, the can *
 * gang up on you!                                       *
.*********************************************************.

'''


# Print BANNER slowly with keyboard sounds for aesthetics
def printer(text):
    mixer.init()
    mixer.music.load("keyboard.mp3")
    mixer.music.play()
    time.sleep(0.5)

    for character in text:
        mixer.music.unpause()
        print(character, end = '')
        if character == '!':
            mixer.music.pause()
            time.sleep(1.7)
        if character in (','):
            mixer.music.pause()
            time.sleep(1.3)
            continue
        time.sleep(0.02)
    mixer.music.pause()
    time.sleep(1)


# Create the main characters, then pass program to main_loop()
def main():
    num_players = int(p_prompt('How many players? ', list('12345678')))
    boss_hp = 20 * num_players
    boss = Boss(name='Boss', lvl=1, hp=boss_hp, at=100, df=0, exp=0)
    boss.MAX_HP = boss_hp
    players = []

    for idx in range(1, num_players + 1):
        player_name = input(f'Player {idx} name: ')
        players.append(MajorCharacter(name=player_name, lvl=1, hp=100, at=10, df=5, exp=0))

    # Boss spawns Minion
    main_loop(boss, players)


# Where the battles happen
def main_loop(boss, players):
    # Boss spawns Minion
    boss.spawn()
    print(f'Boss spawned {boss.minions[-1]}')
    player_options = '\n1. Attack\n2. Charge\n3. Shield'

    # Loop through players, and ask what they want to do
    for player in players:
        time.sleep(1.5)
        prompt = f'''{player_options}\n{player.name}, what would you like to do? '''
        action = p_prompt(prompt, list('123'))

        # If player wants to attack, print all minions and prompt for player choice
        # Than attack the chosen minion
        if action == '1':
            # Create the printed list of minions
            # TODO: Consider creating a function to print ordered choices
            list_of_minions = ''
            for index, minion in enumerate(boss.minions, start = 1):
                list_of_minions += f'{index}. {repr(minion)}\n'
            # If there are no minions, attack the boss
            if not list_of_minions:
                print(f'1. {repr(boss)}')
                player.attack(boss)
                if boss.hp == 0:
                    print('You win!')
                    return
            # If there are minions, ask the user for a choice and attack the chosen minion
            else:
                prompt = f'''{list_of_minions}{player.name}, who would you like to attack? '''
                choice = p_prompt(prompt, [str(i) for i in range(1, len(boss.minions) + 1)])
                target = boss.minions[int(choice) - 1]
                player.attack(target)
                if target.hp == 0:
                    del (boss.minions[int(choice) - 1])

        elif action == '2':
            player.charge()

        elif action == '3':
            player.shield()

    # if there are minions, the minions attack the last player in the list
    if len(boss.minions) == 0:
        print("There are no Minions to attack.")
    for minion in boss.minions:
        minion.attack(players[-1])
        if players[-1].hp == 0:
            del (players[-1])
            if len(players) == 0:
                print("You lose.")
                return

    main_loop(boss, players)


# Persistently prompt the user until user input is in "lst"
def p_prompt(prompt, lst):
    while True:
        ans = input(prompt)

        # Option for quitting the game
        if ans.lower() == 'quit':
            ans = input('Are you sure? (Y|N) ')
            if ans.lower() == 'y':
                sys.exit()
            else:
                continue

        if ans not in lst:
            print('Invalid choice!')
            print()
            continue
        return ans


# Base character class
class Character:
    SHIELD = 0
    CHARGE = False

    # Assign parameters
    def __init__(self, name, lvl=1, hp=100, at=10, df=1, exp=0):
        self.name = name
        self.lvl = lvl
        self.hp = hp
        self.MAX_HP = hp
        self.at = at
        self.df = df
        self.exp = exp

    # First check the defender's shield; if > 0, decrement it, else attack.
    def attack(self, character):
        if character.SHIELD > 0:
            character.SHIELD -= 1
            print(
                f"{self.name} attacked {character.name}. {self.name}'s HP: {self.hp}\{self.MAX_HP}. {character.name}'s HP: {character.hp}\{character.MAX_HP}")
            return

        # If CHARGE is true: attack coefficient "coeff" = 2.5 "( max(2.5, 1) )", else coeff = 1 "( max(0, 1) )"
        coeff = max(int(self.CHARGE) * 2.5, 1)
        character.hp -= (coeff * self.at - character.df)
        character.hp = max(int(character.hp), 0)
        print(
            f"{self.name} attacked {character.name}. {self.name}'s HP: {self.hp}\{self.MAX_HP}. {character.name}'s HP: {character.hp}\{character.MAX_HP}")
        if character.hp <= 0:
            print(f'{character.name} has been defeated!')

        self.CHARGE = False

    # Output: "<character> (HP #)", eg. Boss (HP 20)
    def __repr__(self):
        return (f"{self.name} (HP {self.hp})")

    # Output: "<character> (HP #, AT #, DF #)"
    def __str__(self):
        return (f"{self.name} (HP {self.hp}, AT {self.at}, DF {self.df})")


class MajorCharacter(Character):

    # Recover an "n" amount of HP
    def recover(self, n):
        self.hp += n
        if self.hp > self.MAX_HP:
            self.hp = self.MAX_HP
        print(f"{self.name}'s HP has been restored to {self.hp}/{self.MAX_HP}")

    def fullheal(self):
        self.hp = self.MAX_HP
        print(f"{self.name}'s HP has been fully restored {self.MAX_HP}/{self.MAX_HP}")

    # When called, SHIELD variable is set to 3 only if it was equal to 0. Otherwise, player loses turn
    def shield(self):

        if self.SHIELD == 0:
            self.SHIELD = 3
            print(f"{self.name} is safe from the next 3 attacks.")
            return

        print(f"{self.name} still has a shield of {self.SHIELD}")

    def charge(self):
        self.CHARGE = True
        print(f"{self.name} charged.")


# Although this class is empty, it is useful to group Minions in their own class for future development.
class Minion(Character):
    pass


class Boss(Character):
    minions = []

    # Output of spawn():
    # [Minion instance, Minion instance, Minion instance, etc.]
    def spawn(self):
        self.minions.append(
            Minion(name='Minion', hp=int(self.MAX_HP / 4), at=int(self.at / 4), df=0, lvl=self.lvl, exp=0))


if __name__ == '__main__':
    printer(BANNER_1)
    printer(BANNER_2)
    print("To leave the game, enter 'quit' as an answer.")
    print('Enjoy!!')
    time.sleep(1)
    print()
    main()
