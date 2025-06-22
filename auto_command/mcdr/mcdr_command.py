

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.task.task_manager import TaskManager


class CommandManager:
    def __init__(self, ctx: Context, task_manager: TaskManager):
        self._svc = ctx.svc
        self._cfg = ctx.cfg
        self._tm = task_manager

    def construct_command_tree(self):

        search_cmd_stack = QuotableText('keyword'). \
            runs(lambda src, ctx: self._tm.list_command_stack(src, keyword=ctx['keyword'])). \
            then(Integer('page').runs(lambda src, ctx: self._tm.list_command_stack(src, keyword=ctx['keyword'], page=ctx['page'])))

        self._svc.register_command(
            Literal(self._cfg.prefix).
            runs(self._tm.print_simple_help_message).
            then(
                Literal('help').
                runs(self._tm.print_full_help_message)
            ).
            then(
                Literal('list').
                runs(self._tm.list_command_stack).
                then(
                    Integer('page').at_min(1).
                    runs(lambda src, ctx: self._tm.list_command_stack(src, page=ctx['page']))
                )
            ).
            then(
                Literal('search').then(search_cmd_stack)
            ).
            then(
                search_cmd_stack  # for lazy_man
            ).
            then(
                Literal('send').
                then(
                    QuotableText('name').
                    runs(lambda src, ctx: self._tm.send_command_stack(src, ctx['name'])).
                    then(
                        Literal('async').
                        then(
                            Literal('if').
                            then(
                                GreedyText('condition').
                                runs(lambda src, ctx: self._tm.send_command_stack(src, ctx['name'], ctx['condition']))
                            )
                        ).
                        then(
                            Literal('unless').
                            then(
                                GreedyText('condition').
                                runs(lambda src, ctx: self._tm.send_command_stack(src, ctx['name'], ctx['condition'], True))
                            )
                        )
                    ).
                    then(
                        Literal('if').
                        then(
                            GreedyText('condition').
                            runs(lambda src, ctx: self._tm.send_command_stack(src, ctx['name'], ctx['condition']))
                        )
                    ).
                    then(
                        Literal('unless').
                        then(
                            GreedyText('condition').
                            runs(lambda src, ctx: self._tm.send_command_stack(src, ctx['name'], ctx['condition'], True))
                        )
                    )
                )
            ).
            then(
                Literal('make').
                then(
                    QuotableText('name').
                    then(
                        Integer('perm').in_range(0, 4).
                        runs(lambda src, ctx: self._tm.make_command_stack(src, ctx['name'], ctx['perm'])).
                        then(
                            Text('time').
                            runs(lambda src, ctx: self._tm.make_command_stack(src, ctx['name'], ctx['perm'], ctx['time'])).
                            then(
                                GreedyText('description').
                                runs(lambda src, ctx: self._tm.make_command_stack(src, ctx['name'], ctx['perm'], ctx['time'], ctx['description']))
                            )
                        )
                    )
                )
            ).
            then(
                Literal('del').
                then(
                    QuotableText('name').
                    runs(lambda src, ctx: self._tm.del_command_stack(src, ctx['name']))
                )
            ).
            then(
                Literal('stack').
                then(
                    QuotableText('name').
                    runs(lambda src, ctx: self._tm.info_command_stack(src, ctx['name'])).
                    then(
                        Literal('add').
                        then(
                            GreedyText('command').
                            runs(lambda src, ctx: self._tm.stack_add_command(src, ctx['name'], ctx['command']))
                        )
                    ).
                    then(
                        Literal('before').
                        then(
                            Integer('line').at_min(1).
                            then(
                                GreedyText('command').
                                runs(lambda src, ctx: self._tm.stack_add_command(src, ctx['name'], ctx['command'], ctx['line']))
                            )
                        )
                    ).
                    then(
                        Literal('edit').
                        then(
                            Integer('line').at_min(1).
                            then(
                                GreedyText('command').
                                runs(lambda src, ctx: self._tm.stack_edit_command(src, ctx['name'], ctx['command'], ctx['line']))
                            )
                        )
                    ).
                    then(
                        Literal('del').
                        runs(lambda src, ctx: self._tm.stack_del_command(src, ctx['name'])).
                        then(
                            Integer('line').at_min(1).
                            runs(lambda src, ctx: self._tm.stack_del_command(src, ctx['name'], ctx['line']))
                        )
                    ).
                    then(
                        Literal('rename').
                        then(
                            QuotableText('new_name').
                            runs(lambda src, ctx: self._tm.stack_change_name(src, ctx['name'], ctx['new_name']))
                        )
                    ).
                    then(
                        Literal('perm').
                        then(
                            Integer('level').in_range(0, 4).
                            runs(lambda src, ctx: self._tm.stack_change_perm(src, ctx['name'], ctx['level']))
                        )
                    ).
                    then(
                        Literal('interval').
                        then(
                            Text('time').
                            runs(lambda src, ctx: self._tm.stack_change_interval(src, ctx['name'], ctx['time']))
                        )
                    ).
                    then(
                        Literal('desc').
                        then(
                            QuotableText('description').
                            runs(lambda src, ctx: self._tm.stack_change_desc(src, ctx['name'], ctx['description']))
                        )
                    ).
                    then(
                        Literal('record').
                        runs(lambda src, ctx: self._tm.stack_record(src, ctx['name']))
                    )
                )
            ).
            then(
                Literal('wait').
                then(
                    Text('time').
                    runs(lambda src, ctx: self._tm.print_wait_help(src, ctx['time']))
                )
            ).
            then(
                Literal('white').
                then(
                    GreedyText('regex').
                    runs(lambda src, ctx: self._tm.print_perm_help(src, ctx['regex']))
                )
            ).
            then(
                Literal('black').
                then(
                    GreedyText('regex').
                    runs(lambda src, ctx: self._tm.print_perm_help(src, ctx['regex'], False))
                )
            )
        )
