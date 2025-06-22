from typing import Optional, List
import re

from mcdreforged.api.all import *

from auto_command.mcdr.mcdr_service import Service
from auto_command.config import Config
from auto_command.exceptions import ACExceptionBase, ACRecursionException, ACStackExistsException, ACPermDeniedException


class Utils:
    def __init__(self, svc: Service, cfg: Config):
        self._svc = svc
        self._cfg = cfg

    def click_info(self, text: RText, name: Optional[str] = None) -> RText:
        if not name:
            name = text.to_plain_text()
        return text.h(self._svc.tr('command_stack_info.display')).c(RAction.run_command, f'{self._cfg.prefix} stack {name}')

    def req_perm(self, source: CommandSource, perm):
        if source.is_player and not source.has_permission(perm):
            raise ACPermDeniedException(perm, source.get_permission_level())

    def click_send(self, text: RText, name: Optional[str] = None) -> RText:
        if not name:
            name = text.to_plain_text()
        return text.h(self._svc.tr('command_stack_info.send.hover')).c(RAction.run_command, f'{self._cfg.prefix} send {name}')

    def get_exception_msg(self, e: Exception) -> RTextBase:
        try:
            raise e
        except ACRecursionException as e:
            recursion: List[RText] = []
            for name in e.args[0]:
                recursion.append(self.click_info(name))
                recursion.append(RText(' -> '))
            recursion.pop()
            msg = RTextList()
            for s in recursion:
                msg.append(s)
            return self._svc.tr(e.translation_key, msg)
        except ACStackExistsException as e:
            return self._svc.tr(e.translation_key, self.click_info(RText(e.args[0], RColor.gold)))
        except ACExceptionBase as e:
            return self._svc.tr(e.translation_key, *e.args)
        except Exception as e:
            return RText(e)

    def get_source_dimension(self, source: PlayerCommandSource):
        api = self._svc.get_mc_data_api()
        dims = ['overworld', 'the_end', 'the_nether']
        return dims[api.get_player_dimension(source.player)]

    def interpret_player_spawn(self, source: CommandSource, command: str) -> str:
        carpet_bot = re.match(r'^/player (.*) spawn', command)
        if carpet_bot and isinstance(source, PlayerCommandSource):
            api = self._svc.get_mc_data_api()
            pos = api.get_player_coordinate(source.player)
            face = api.get_player_info(source.player, 'Rotation')
            dims = ['overworld', 'the_end', 'the_nether']
            dim = dims[api.get_player_dimension(source.player)]
            gamemodes = ['survival', 'creative', 'adventure', 'spectator']
            gamemode = gamemodes[api.get_player_info(source.player, 'playerGameType')]
            bot = carpet_bot.group(1)
            nodes = command.split(' ')
            if len(nodes) > 4 and nodes[3] == 'in':
                gamemode = nodes[4]
            elif len(nodes) > 6 and nodes[3] == 'at':
                pos = nodes[4:7]
                if len(nodes) > 9 and nodes[7] == 'facing':
                    face = nodes[8:10]
                    if len(nodes) > 11 and nodes[10] == 'in':
                        dim = nodes[11]
                        if len(nodes) > 13 and nodes[12] == 'in':
                            gamemode = nodes[13]
            facing = f'{face[0]} {face[1]}'
            command = f'/player {bot} spawn at {pos[0]} {pos[1]} {pos[2]} facing {facing} in {dim} in {gamemode}'
        return command

    def get_user(self, source) -> str:
        if isinstance(source, PlayerCommandSource):
            return source.player
        else:
            return 'Console'
