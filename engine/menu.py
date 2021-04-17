from typing import List, Dict

from bearlibterminal import terminal

from config import Config


class MenuOption:
    def __init__(self, is_human: bool, cpu_lvl: int):
        self.is_human = is_human
        self.cpu_lvl = cpu_lvl


class GameStartException(Exception):
    def __init__(self, player_options: Dict[int, MenuOption]):
        self.player_options = player_options


class Menu:
    def __init__(self, row, col):
        self._row = row
        self._col = col
        self._current_player = 0
        self._player_options = dict()
        self.update_player()

    def loop(self):
        current_options = self._player_options[self._current_player]
        terminal.clear()
        terminal.puts(
            self._col, self._row - 2,
            str.format('TERMCHESS'),
        )
        terminal.puts(
            self._col - 6, self._row,
            str.format(self._render(player=1)),
        )
        terminal.puts(
            self._col - 6, self._row + 1,
            str.format(self._render(player=2)),
        )
        terminal.puts(
            self._col - 14, self._row + 3,
            str.format('[color=grey][[ENTER: Confirm]] [[LEFT/RIGHT: Select]]'),
        )
        if not current_options.is_human:
            terminal.puts(
                self._col - 9, self._row + 4,
                str.format('[color=grey][[UP/DOWN: Select CPU level]]'),
            )
        terminal.refresh()
        key = terminal.read()
        if key == terminal.TK_CLOSE:
            raise SystemExit()
        if key == terminal.TK_ESCAPE:
            if self._current_player == 2:
                self._current_player = 1
                del self._player_options[2]
        elif key == terminal.TK_LEFT or key == terminal.TK_RIGHT:
            new_menu_option = MenuOption(is_human=not current_options.is_human, cpu_lvl=current_options.cpu_lvl)
            self._player_options[self._current_player] = new_menu_option
        elif key == terminal.TK_UP:
            if not current_options.is_human:
                new_cpu_lvl = min(current_options.cpu_lvl + 1, 20)
                new_menu_option = MenuOption(is_human=current_options.is_human, cpu_lvl=new_cpu_lvl)
                self._player_options[self._current_player] = new_menu_option
        elif key == terminal.TK_DOWN:
            if not current_options.is_human:
                new_cpu_lvl = max(current_options.cpu_lvl - 1, 0)
                new_menu_option = MenuOption(is_human=current_options.is_human, cpu_lvl=new_cpu_lvl)
                self._player_options[self._current_player] = new_menu_option
        elif key == terminal.TK_RETURN:
            self.update_player()
            return

    def update_player(self):
        self._current_player += 1
        self._player_options[self._current_player] = MenuOption(is_human=True, cpu_lvl=10)
        if self._current_player > 2:
            raise GameStartException(player_options=self._player_options)

    def _render(self, player):
        player_has_options = player in self._player_options.keys()
        player_options = self._player_options.get(player)
        if player_has_options and not player_options.is_human:
            player_options = self._player_options[player]
            cpu_text = str.format('lvl {}', str(player_options.cpu_lvl))
        else:
            cpu_text = 'cpu'

        if player != self._current_player:
            selected_color = str.format('[color={}]', Config.SELECTED_COLOR)
        else:
            selected_color = '[color=white]'

        if player_has_options:
            human_opt_color = selected_color if player_options.is_human else '[color=gray]'
            cpu_opt_color = selected_color if not player_options.is_human else '[color=gray]'
        else:
            human_opt_color = ''
            cpu_opt_color = ''

        player_color = '[color=white]' if player == self._current_player else '[color=gray]'
        return str.format('{}player {}: {}human [color=gray]/ {}{}', player_color, player, human_opt_color,
                          cpu_opt_color, cpu_text)
