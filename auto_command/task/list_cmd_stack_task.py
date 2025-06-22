from math import ceil
from typing import Optional

from mcdreforged.api.all import *

from auto_command.context import Context
from auto_command.storage.storage import CommandStackStorage


class ListCommandStackTask:
    def __init__(self, ctx: Context, storage: CommandStackStorage):
        self._cfg = ctx.cfg
        self._svc = ctx.svc
        self._utils = ctx.utils
        self._storage = storage

    def list_command_stack(self, source: CommandSource, keyword: Optional[str] = None, page: Optional[int] = None):
        matched_stack_names = self._storage.stack_names() if keyword is None else self._storage.search_stack(keyword)
        matched_count = len(matched_stack_names)
        page_count = ceil(matched_count / self._cfg.stack_per_page)
        if keyword is None:
            lit = 'list'
        else:
            lit = 'search'

        def const_line(stack_name):
            stack = self._storage.get(stack_name)
            line = RTextList()
            line.append(self._utils.click_send(RText('[▷]', RColor.green), stack_name))
            line.append(' ')
            line.append(self._utils.click_info(RText(stack_name, RColor.gold)))
            line.append(' ')
            line.append(RText(stack.perm, RColor.light_purple).h(self._svc.tr('list_command_stack.perm_hover')))
            if not (stack.interval == '0' or stack.interval == ''):
                line.append(' ')
                line.append(RText(stack.interval, RColor.aqua).h(self._svc.tr('list_command_stack.interval_hover')))
            line.append(' ')
            line.append(RText('[i]', RColor.gray).h(stack.desc))
            return line

        if page is None:
            for name in matched_stack_names:
                self._svc.print(source, const_line(name), prefix=RText('- ', RColor.gray))

        else:
            if page > page_count:
                page = page_count
            left, right = (page - 1) * self._cfg.stack_per_page, page * self._cfg.stack_per_page
            for i in range(left, right):
                if 0 <= i < matched_count:
                    self._svc.print(source, const_line(matched_stack_names[i]), prefix=RText('- ', color=RColor.gray))

            has_prev = page != 1
            has_next = page != page_count
            color = {False: RColor.dark_gray, True: RColor.gray}
            if keyword is None:
                keyword = ''
            else:
                keyword += ' '

            prev_page = RText('<-', color=color[has_prev])
            if has_prev:
                prev_page.h(self._svc.tr('list_command_stack.page_prev.Y')). \
                    c(RAction.run_command, f'{self._cfg.prefix} {lit} {keyword}{page - 1}')
            else:
                prev_page.h(self._svc.tr('list_command_stack.page_prev.N'))

            next_page = RText('->', color=color[has_next])
            if has_next:
                next_page.h(self._svc.tr('list_command_stack.page_next.Y')). \
                    c(RAction.run_command, f'{self._cfg.prefix} {lit} {keyword}{page + 1}')
            else:
                next_page.h(self._svc.tr('list_command_stack.page_next.N'))

            source.reply(RTextList(
                prev_page,
                f' §a{page}§r/§a{page_count} ',
                next_page
            ))

        self._svc.print(source, self._svc.tr(f'list_command_stack.count.{lit}', matched_count))
