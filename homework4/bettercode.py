"""
Прогнал свой код через гпт, чтобы он улучшил и получилось весело))
"""
from __future__ import annotations
import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# -----------------------------
# Константы и утилиты
# -----------------------------
DIRS = {
    'w': (-1, 0),
    's': (1, 0),
    'a': (0, -1),
    'd': (0, 1),
}

SYMBOLS = {
    'player': '☺',
    'empty': '.',
    'chest': '☐',
    'monster': 'M',
    'trap': '^',
    'portal': 'O',
    'key': 'K',
    'unknown': '?'
}

def clamp(v, a, b):
    return max(a, min(b, v))

def roll(minv, maxv):
    return random.randint(minv, maxv)

# -----------------------------
# Items / Equipment / Consumables
# -----------------------------
@dataclass
class Item:
    name: str
    desc: str

@dataclass
class Weapon(Item):
    atk: int = 0

@dataclass
class Armor(Item):
    defense: int = 0

@dataclass
class Consumable(Item):
    heal: int = 0
    # можно расширить (бонусы и т.д.)

# -----------------------------
# Enemy
# -----------------------------
@dataclass
class Enemy:
    name: str
    hp: int
    atk: int
    defense: int
    exp: int = 0

    def take_damage(self, dmg: int) -> int:
        dmg = max(0, dmg - self.defense)
        self.hp -= dmg
        return dmg

    def is_alive(self) -> bool:
        return self.hp > 0

# -----------------------------
# Room and Dungeon
# -----------------------------
@dataclass
class Room:
    kind: str  # 'empty', 'chest', 'monster', 'trap', 'portal', 'key'
    seen: bool = False
    explored: bool = False  # если игрок когда-либо заходил
    chest_locked: bool = False
    chest_contents: List[Item] = field(default_factory=list)
    enemy: Optional[Enemy] = None
    trap_damage: int = 0
    portal_enabled: bool = False

    def symbol_for_map(self, reveal_traps=False):
        if self.kind == 'empty':
            return SYMBOLS['empty']
        if self.kind == 'chest':
            return SYMBOLS['chest']
        if self.kind == 'monster':
            return SYMBOLS['monster']
        if self.kind == 'trap':
            return SYMBOLS['trap'] if (reveal_traps or self.explored) else SYMBOLS['empty']
        if self.kind == 'portal':
            return SYMBOLS['portal']
        if self.kind == 'key':
            return SYMBOLS['key']
        return SYMBOLS['unknown']

@dataclass
class Dungeon:
    n: int
    m: int
    grid: List[List[Room]] = field(init=False)
    portal_pos: Tuple[int, int] = field(init=False)
    key_pos: Tuple[int, int] = field(init=False)
    seed: Optional[int] = None
    difficulty: int = 1

    def __post_init__(self):
        if self.seed is not None:
            random.seed(self.seed)
        self.grid = [[Room(kind='empty') for _ in range(self.m)] for __ in range(self.n)]
        self.portal_pos = (0, 0)
        self.key_pos = (0, 0)
        self.generate_contents()

    def generate_contents(self):
        # probabilities варьируются с уровнем difficulty
        for i in range(self.n):
            for j in range(self.m):
                self.grid[i][j] = Room(kind='empty')

        # Place portal (disabled until key found)
        px, py = self.random_cell(exclude_center=True)
        self.portal_pos = (px, py)
        self.grid[px][py].kind = 'portal'
        self.grid[px][py].portal_enabled = False

        # Place key somewhere else (maybe chest or key-room)
        kx, ky = self.random_cell(exclude={(px,py)}, exclude_center=True)
        self.key_pos = (kx, ky)
        self.grid[kx][ky].kind = 'key'

        # Place some chests, enemies, traps
        count = max( (self.n*self.m)//6, 4 )
        for _ in range(count):
            x,y = self.random_cell(exclude={(px,py),(kx,ky)})
            choice = random.choices(['chest','monster','trap','empty'], weights=[30,40,20,10])[0]
            if choice == 'chest':
                room = Room(kind='chest', chest_locked=random.random() < 0.5)
                room.chest_contents = self.generate_loot()
                self.grid[x][y] = room
            elif choice == 'monster':
                enemy = self.generate_enemy()
                room = Room(kind='monster', enemy=enemy)
                self.grid[x][y] = room
            elif choice == 'trap':
                dmg = roll(2 + self.difficulty, 5 + self.difficulty*3)
                room = Room(kind='trap', trap_damage=dmg)
                self.grid[x][y] = room
            # empty ignored

    def random_cell(self, exclude: set = None, exclude_center=False):
        if exclude is None:
            exclude = set()
        attempts = 0
        while True:
            x = random.randint(0, self.n-1)
            y = random.randint(0, self.m-1)
            if exclude_center:
                cx, cy = self.n//2, self.m//2
                if (x,y) == (cx,cy):
                    attempts += 1
                    if attempts > 200:
                        break
                    continue
            if (x,y) in exclude:
                attempts += 1
                if attempts > 200:
                    break
                continue
            return (x,y)
        # fallback
        for i in range(self.n):
            for j in range(self.m):
                if (i,j) not in exclude:
                    return (i,j)
        return (0,0)

    def generate_loot(self) -> List[Item]:
        loot = []
        # higher difficulty → better loot chances
        r = random.randint(0, 100)
        if r < 40:
            # consumable
            heal = roll(5 + self.difficulty*2, 20 + self.difficulty*3)
            loot.append(Consumable(name='Зелье', desc=f'Восстанавливает {heal} HP', heal=heal))
        elif r < 70:
            # weapon
            atk = roll(1 + self.difficulty, 3 + self.difficulty*2)
            loot.append(Weapon(name=f'Оружие +{atk}', desc=f'+{atk} к атаке', atk=atk))
        else:
            # armor
            df = roll(1 + self.difficulty, 3 + self.difficulty*2)
            loot.append(Armor(name=f'Доспех +{df}', desc=f'+{df} к броне', defense=df))
        # sometimes add coins or another item
        if random.random() < 0.2:
            loot.append(Consumable(name='Малое зелье', desc='Малое восстановление', heal=roll(3,8)))
        return loot

    def generate_enemy(self) -> Enemy:
        # enemy scales with difficulty
        base_hp = roll(5 + self.difficulty*2, 8 + self.difficulty*4)
        atk = roll(1 + self.difficulty, 2 + self.difficulty*2)
        df = roll(0, self.difficulty)
        return Enemy(name=f'Гоблин L{self.difficulty}', hp=base_hp, atk=atk, defense=df, exp=5 + self.difficulty*2)

    def reveal_portal_if_key(self):
        px, py = self.portal_pos
        self.grid[px][py].portal_enabled = True
        # change description (visual handled in map)

# -----------------------------
# Player
# -----------------------------
@dataclass
class Player:
    x: int
    y: int
    hp_max: int = 100
    hp: int = 100
    atk_base: int = 2
    def_base: int = 0
    weapon: Optional[Weapon] = None
    armor: Optional[Armor] = None
    inventory: List[Item] = field(default_factory=list)
    keys: int = 0
    level: int = 1
    exp: int = 0

    def attack_value(self):
        return self.atk_base + (self.weapon.atk if self.weapon else 0)

    def defense_value(self):
        return self.def_base + (self.armor.defense if self.armor else 0)

    def take_damage(self, dmg: int) -> int:
        dmg = max(0, dmg - self.defense_value())
        self.hp -= dmg
        return dmg

    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount:int):
        self.hp = clamp(self.hp + amount, 0, self.hp_max)

    def equip(self, item: Item) -> str:
        if isinstance(item, Weapon):
            old = self.weapon.name if self.weapon else None
            self.weapon = item
            return f"Экипировано оружие {item.name}. (Старое: {old})"
        if isinstance(item, Armor):
            old = self.armor.name if self.armor else None
            self.armor = item
            return f"Экипирована броня {item.name}. (Старая: {old})"
        return "Это нельзя экипировать."

    def add_item(self, item: Item):
        self.inventory.append(item)

    def use_consumable(self, idx:int) -> str:
        if idx < 0 or idx >= len(self.inventory):
            return "Неверный индекс."
        item = self.inventory[idx]
        if not isinstance(item, Consumable):
            return "Это не расходник."
        self.heal(item.heal)
        self.inventory.pop(idx)
        return f"Использовано {item.name}, +{item.heal} HP."

# -----------------------------
# Game engine
# -----------------------------
class Game:
    def __init__(self):
        self.level = 1
        self.dungeon = None  # type: Dungeon
        self.player = None   # type: Player
        self.init_new_level(self.level)

    def init_new_level(self, level:int):
        print(f"\n--- Переход на уровень {level} ---")
        n = random.randint(5, 8)
        m = random.randint(5, 8)
        self.dungeon = Dungeon(n=n, m=m, difficulty=level)
        # player starts in center
        sx, sy = n//2, m//2
        if self.player is None:
            # new player
            self.player = Player(x=sx, y=sy, hp_max=100, hp=100, atk_base=2, def_base=0)
        else:
            # keep stats; reposition to center and heal a bit
            self.player.x, self.player.y = sx, sy
            self.player.hp = clamp(self.player.hp + max(5, 10 - level), 0, self.player.hp_max)
        # ensure center is empty
        self.dungeon.grid[sx][sy] = Room(kind='empty')
        print(f"Размер уровня: {n}x{m}. Вы стартуете в ({sx},{sy}).")
        # chance to give a starter consumable each level
        if random.random() < 0.7:
            heal = roll(6, 18)
            potion = Consumable(name='Зелье', desc=f'Восстанавливает {heal} HP', heal=heal)
            self.player.add_item(potion)
            print(f"В ваш инвентарь положено стартовое зелье: {potion.name} (+{potion.heal} HP).")

    def render_map(self, reveal_traps=False):
        n,m = self.dungeon.n, self.dungeon.m
        print("\nКарта (P — вы):")
        for i in range(n):
            line = []
            for j in range(m):
                if (i,j) == (self.player.x, self.player.y):
                    line.append(SYMBOLS['player'])
                else:
                    r = self.dungeon.grid[i][j]
                    # don't reveal monsters/traps unless explored (or reveal_traps True)
                    if r.kind == 'monster' and not r.explored:
                        line.append(SYMBOLS['empty'])
                    else:
                        line.append(r.symbol_for_map(reveal_traps=reveal_traps))
            print(' '.join(line))
        print()

    def show_status(self):
        print(f"HP: {self.player.hp}/{self.player.hp_max}  ATK: {self.player.attack_value()}  DEF: {self.player.defense_value()}  Keys: {self.player.keys}  Level: {self.level}  EXP: {self.player.exp}")

    def show_inventory(self):
        if not self.player.inventory:
            print("Инвентарь пуст.")
            return
        print("Инвентарь:")
        for idx, it in enumerate(self.player.inventory):
            t = type(it).__name__
            if isinstance(it, Weapon):
                stat = f"ATK+{it.atk}"
            elif isinstance(it, Armor):
                stat = f"DEF+{it.defense}"
            elif isinstance(it, Consumable):
                stat = f"HEAL+{it.heal}"
            else:
                stat = ''
            print(f" {idx}: {it.name} ({t}) {stat} — {it.desc}")

    def step(self, cmd:str) -> bool:
        """Возвращает True если игра продолжается, False если закончилась"""
        cmd = cmd.strip().lower()
        if cmd in ('q','quit','exit'):
            print("Выход из игры.")
            return False
        if cmd == 'map':
            self.render_map()
            return True
        if cmd == 'inv':
            self.show_inventory()
            return True
        if cmd.startswith('use'):
            # use <index>
            parts = cmd.split()
            if len(parts) < 2:
                print("Использование: use <индекс_инвентаря>")
                return True
            try:
                idx = int(parts[1])
            except:
                print("Неверный индекс.")
                return True
            print(self.player.use_consumable(idx))
            return True
        if cmd.startswith('equip'):
            parts = cmd.split()
            if len(parts) < 2:
                print("Экипировка: equip <индекс_инвентаря>")
                return True
            try:
                idx = int(parts[1])
            except:
                print("Неверный индекс.")
                return True
            if idx < 0 or idx >= len(self.player.inventory):
                print("Неверный индекс.")
                return True
            item = self.player.inventory.pop(idx)
            print(self.player.equip(item))
            return True
        # movement
        if cmd in DIRS:
            dx, dy = DIRS[cmd]
            nx = self.player.x + dx
            ny = self.player.y + dy
            if not (0 <= nx < self.dungeon.n and 0 <= ny < self.dungeon.m):
                print("Нельзя идти в эту сторону — граница уровня.")
                return True
            # move
            self.player.x, self.player.y = nx, ny
            room = self.dungeon.grid[nx][ny]
            room.explored = True
            # handle room
            return self.handle_room(room)
        print("Команда не распознана. w/a/s/d - ход, map - карта, inv - инвентарь, use N, equip N, q - выход")
        return True

    def handle_room(self, room: Room) -> bool:
        # if portal
        if room.kind == 'portal':
            if room.portal_enabled:
                print("Вы вошли в портал! Переход на следующий уровень...")
                self.level += 1
                self.init_new_level(self.level)
                # regenerate dungeon and continue
                return True
            else:
                print("Вы видите портал, но он неактивен — нужен ключ.")
                return True
        if room.kind == 'key':
            print("Вы нашли ключ! Добавлен в инвентарь.")
            self.player.keys += 1
            room.kind = 'empty'
            # Reveal portal
            self.dungeon.reveal_portal_if_key()
            return True
        if room.kind == 'empty':
            print("Пустая комната.")
            return True
        if room.kind == 'chest':
            # open chest
            if room.chest_locked:
                if self.player.keys > 0:
                    print("Сундук заперт. У вас есть ключ. Использовать ключ? (y/n)")
                    ans = input("> ").strip().lower()
                    if ans == 'y':
                        self.player.keys -= 1
                        print("Вы открыли сундук ключом.")
                        found = room.chest_contents
                        for it in found:
                            print(f" - найдено: {it.name} — {it.desc}")
                            self.player.add_item(it)
                        room.kind = 'empty'
                        room.chest_contents = []
                        return True
                    else:
                        print("Вы оставили сундук закрытым.")
                        return True
                else:
                    print("Сундук заперт, но у вас нет ключа.")
                    return True
            else:
                print("Вы открыли сундук.")
                if not room.chest_contents:
                    print("Сундук пуст.")
                    room.kind = 'empty'
                    return True
                for it in room.chest_contents:
                    print(f" - найдено: {it.name} — {it.desc}")
                    self.player.add_item(it)
                room.kind = 'empty'
                room.chest_contents = []
                return True
        if room.kind == 'trap':
            # hidden traps might be unseen until explored; damage when stepped
            dmg = room.trap_damage
            print(f"Ловушка! Вы получили {dmg} единиц урона.")
            real_dmg = self.player.take_damage(dmg)
            print(f"Фактический урон с учётом брони: {real_dmg}. Текущее HP: {self.player.hp}/{self.player.hp_max}")
            room.kind = 'empty'  # одноразовая
            if not self.player.is_alive():
                print("Вы погибли в ловушке.")
                return self.game_over()
            return True
        if room.kind == 'monster':
            e = room.enemy
            if e is None:
                print("Комната пуста (монстр уже побеждён).")
                room.kind = 'empty'
                return True
            print(f"В комнате — {e.name}! (HP {e.hp}, ATK {e.atk}, DEF {e.defense})")
            # combat loop
            while e.is_alive() and self.player.is_alive():
                print("\nВыберите действие: hit (атака), flee (убежать), stats (статусы), inv, equip, use N")
                action = input("> ").strip().lower()
                if action in ('hit', 'h', ''):
                    # player attack
                    atk = self.player.attack_value()
                    dmg_dealt = e.take_damage(atk)
                    print(f"Вы атакуете (`{atk}`) и наносите {dmg_dealt} урона. Монстр HP: {max(0,e.hp)}")
                    if not e.is_alive():
                        print(f"Вы победили {e.name}! Получено {e.exp} опыта.")
                        self.player.exp += e.exp
                        # maybe drop loot
                        if random.random() < 0.5:
                            loot = self.dungeon.generate_loot()
                            for it in loot:
                                self.player.add_item(it)
                                print(f"Добыча: {it.name} — {it.desc}")
                        room.enemy = None
                        room.kind = 'empty'
                        break
                elif action.startswith('use'):
                    parts = action.split()
                    if len(parts) >= 2:
                        try:
                            idx = int(parts[1])
                            print(self.player.use_consumable(idx))
                        except:
                            print("Неверный индекс.")
                    else:
                        print("use <индекс>")
                    continue
                elif action.startswith('equip'):
                    parts = action.split()
                    if len(parts) >= 2:
                        try:
                            idx = int(parts[1])
                            if idx < 0 or idx >= len(self.player.inventory):
                                print("Неверный индекс.")
                            else:
                                item = self.player.inventory.pop(idx)
                                print(self.player.equip(item))
                        except:
                            print("Неверный индекс.")
                    else:
                        print("equip <индекс>")
                    continue
                elif action in ('flee','run'):
                    # attempt to flee: chance depends on enemy and player
                    chance = 50 + (self.player.attack_value() - e.atk)*5
                    if random.randint(1,100) <= clamp(chance, 10, 90):
                        print("Вам удалось убежать!")
                        # move player back to previous position if possible — we don't track previous easily; instead randomly step to adjacent safe cell
                        moved = self.safe_step_out()
                        return True
                    else:
                        print("Не удалось убежать.")
                elif action == 'stats':
                    self.show_status()
                    print(f"Монстр: {e.name} HP={e.hp}, ATK={e.atk}, DEF={e.defense}")
                    continue
                elif action == 'inv':
                    self.show_inventory()
                    continue
                else:
                    print("Неизвестное действие.")
                    continue
                # if monster still alive, it attacks
                if e.is_alive():
                    dmg = e.atk
                    taken = self.player.take_damage(dmg)
                    print(f"Монстр атакует! Вы получили {taken} урона. HP: {self.player.hp}/{self.player.hp_max}")
                if not self.player.is_alive():
                    print("Вы погибли в бою.")
                    return self.game_over()
            return True
        print("Что-то непонятное в комнате.")
        return True

    def safe_step_out(self) -> bool:
        # try to step to any adjacent cell that is inside bounds
        for dx,dy in DIRS.values():
            nx = self.player.x + dx
            ny = self.player.y + dy
            if 0 <= nx < self.dungeon.n and 0 <= ny < self.dungeon.m:
                self.player.x, self.player.y = nx, ny
                return True
        return True

    def game_over(self) -> bool:
        print("\n=== Игра окончена ===")
        print("1) Начать заново")
        print("2) Выйти")
        ans = input("> ").strip()
        if ans == '1':
            # reset everything
            self.__init__()
            return True
        else:
            print("До свидания!")
            sys.exit(0)

    def main_loop(self):
        print("Добро пожаловать в Dungeon Crawler!")
        print("Команды: w/a/s/d - ходы; map - карта; inv - инвентарь; use N - применить расходник; equip N - экипировать; q - выйти")
        while True:
            self.show_status()
            self.render_map()
            cmd = input("Ваш ход > ")
            cont = self.step(cmd)
            if not cont:
                break

# -----------------------------
# Запуск
# -----------------------------
if __name__ == "__main__":
    # Чтобы игра была чуть более предсказуемой при отладке, можно передать семя через аргументы
    seed = None
    if len(sys.argv) >= 2:
        try:
            seed = int(sys.argv[1])
            random.seed(seed)
        except:
            pass
    game = Game()
    game.main_loop()
