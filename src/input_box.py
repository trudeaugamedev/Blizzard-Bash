# Entire file borrowed from another project :D

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from functools import lru_cache
from pygame.locals import *
import pyperclip
import pygame
import time

from .constants import VEC, STOPPING_CHARS, FONT, TEXT_COLOR
from .sprite import VisibleSprite, Layers

def rm_from_str(string: str, index: int) -> str:
    return string[:index] + string[index + 1:]

def cut_from_str(string: str, r: tuple[int, int]) -> str:
    return string[:r[0]] + string[r[1] + 1:]

def add_to_str(string: str, index: int, insert: str) -> str:
    return string[:index] + insert + string[index:]

class InputBox(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, Layers.GUI)
        self.pos = VEC(pos)
        self.size = VEC(size)

        self.font = FONT[50]
        self.text = ""
        self.undo_history = [("", 0)]
        self.redo_history = []
        self.selecting = False
        self.text_width = 0
        self.text_height = self.font.size(" ")[1]

        self.cursor_blink_time = time.time()
        self.cursor_visible = True
        self.cursor_index = 0
        self.cursor_begin = 0
        self.cursor_pos = VEC(20, 20)

    def update(self) -> None:
        old_index = self.cursor_index
        if self.manager.key_presses[K_LCTRL]:
            self.handle_control()
        self.handle_keys()

        tmp_index = self.cursor_index
        while self.font.size(self.text)[0] > self.size.x - 24:
            self.cursor_index = len(self.text)
            self._backspace()
        self.cursor_index = min(tmp_index, len(self.text))

        if not self.selecting:
            self.cursor_begin = self.cursor_index

        self.cursor_pos = self.calc_cursor_pos(self.cursor_index)
        self.save_to_history(self.text)

        if old_index != self.cursor_index:
            self.cursor_blink_time = time.time()
            self.cursor_visible = True

        if time.time() - self.cursor_blink_time > 0.5:
            self.cursor_blink_time = time.time()
            self.cursor_visible = not self.cursor_visible

    def handle_control(self) -> None:
        for key in self.manager.key_downs.values():
            if key.key == K_BACKSPACE:
                self._ctrl_backspace()
            elif key.key == K_DELETE:
                self._ctrl_delete()
            elif key.key == K_LEFT:
                self._ctrl_left()
            elif key.key == K_RIGHT:
                self._ctrl_right()
            elif key.key == K_a:
                self._ctrl_a()
            elif key.key == K_c:
                self._ctrl_c()
            elif key.key == K_v:
                self._ctrl_v()
            elif key.key == K_x:
                self._ctrl_x()
            elif key.key == K_z:
                self._ctrl_z()
            elif key.key == K_y:
                self._ctrl_y()

    def handle_keys(self) -> None:
        for key in self.manager.key_downs.values():
            if key.unicode.isprintable() and key.unicode:
                self._printables(key)
            elif key.key == K_BACKSPACE:
                self._backspace()
            elif key.key == K_DELETE:
                self._delete()
            elif key.key == K_LEFT:
                self._left()
            elif key.key == K_RIGHT:
                self._right()
            elif key.key == K_LSHIFT:
                self._shift()
            elif key.key == K_HOME:
                self._home()
            elif key.key == K_END:
                self._end()

    def _printables(self, key: pygame.event.Event) -> None:
        self.remove_selected()
        self.text = add_to_str(self.text, self.cursor_index, key.unicode)
        self.cursor_index += 1

    def _backspace(self) -> None:
        if self.cursor_index <= 0 and not self.selecting: return
        if self.remove_selected(): return
        self.text = rm_from_str(self.text, self.cursor_index - 1)
        self.cursor_index -= 1

    def _delete(self) -> None:
        if self.remove_selected(): return
        self.text = rm_from_str(self.text, self.cursor_index)

    def _left(self) -> None:
        if self.cursor_index > 0 and (self.manager.key_presses[K_LSHIFT] or not self.selecting):
            self.cursor_index -= 1
        else:
            self.selecting = False
            self.cursor_index = self.left_cursor
        if self.manager.key_presses[K_LSHIFT] and self.cursor_begin != self.cursor_index:
            self.selecting = True

    def _right(self) -> None:
        if self.cursor_index < len(self.text) and (self.manager.key_presses[K_LSHIFT] or not self.selecting):
            self.cursor_index += 1
        else:
            self.selecting = False
            self.cursor_index = self.right_cursor
        if self.manager.key_presses[K_LSHIFT] and self.cursor_begin != self.cursor_index:
            self.selecting = True

        if self.cursor_index < 0: self.cursor_index = 0
        elif self.cursor_index > len(self.text): self.cursor_index = len(self.text)

    def _shift(self) -> None:
        if not self.selecting:
            self.cursor_begin = self.cursor_index

    def _home(self) -> None:
        self.cursor_index = 0

    def _end(self) -> None:
        self.cursor_index = len(self.text)

    def _ctrl_backspace(self) -> None:
        if self.cursor_index <= 0: return
        if self.remove_selected(): return
        self.text = rm_from_str(self.text, self.cursor_index - 1)
        self.cursor_index -= 1
        while self.cursor_index > 0 and self.text[self.cursor_index - 1] not in STOPPING_CHARS:
            self.text = rm_from_str(self.text, self.cursor_index - 1)
            self.cursor_index -= 1

    def _ctrl_delete(self) -> None:
        if self.cursor_index == len(self.text): return
        if self.remove_selected(): return
        self.text = rm_from_str(self.text, self.cursor_index)
        while self.cursor_index != len(self.text) and self.text[self.cursor_index] not in STOPPING_CHARS:
            self.text = rm_from_str(self.text, self.cursor_index)

    def _ctrl_left(self) -> None:
        if self.cursor_index == 0: return
        self.cursor_index -= 1
        while self.cursor_index > 0 and self.text[self.cursor_index - 1] not in STOPPING_CHARS:
            self.cursor_index -= 1

    def _ctrl_right(self) -> None:
        if self.cursor_index == len(self.text): return
        self.cursor_index += 1
        while self.cursor_index < len(self.text) and self.text[self.cursor_index] not in STOPPING_CHARS:
            self.cursor_index += 1

    def _ctrl_a(self) -> None:
        self.selecting = True
        self.cursor_begin = 0
        self.cursor_index = len(self.text)

    def _ctrl_c(self) -> None:
        if not self.selecting or self.left_cursor == self.right_cursor: return
        pyperclip.copy(self.text[self.left_cursor:self.right_cursor])

    def _ctrl_v(self) -> None:
        self.remove_selected()
        text = pyperclip.paste()
        self.text = add_to_str(self.text, self.cursor_index, text)
        self.cursor_index += len(text)

    def _ctrl_x(self) -> None:
        if not self.selecting or self.left_cursor == self.right_cursor: return
        pyperclip.copy(self.text[self.left_cursor:self.right_cursor])
        self.remove_selected()

    def _ctrl_z(self) -> None:
        if len(self.undo_history) <= 1: return
        self.redo_history.append(self.undo_history.pop())
        self.text, self.cursor_index = self.undo_history[-1]

    def _ctrl_y(self) -> None:
        if not self.redo_history: return
        self.undo_history.append(self.redo_history.pop())
        self.text, self.cursor_index = self.undo_history[-1]

    @property
    def left_cursor(self) -> int:
        return min(self.cursor_begin, self.cursor_index)

    @property
    def right_cursor(self) -> int:
        return max(self.cursor_begin, self.cursor_index)

    def calc_cursor_pos(self, cursor_index: int) -> VEC:
        cursor_pos = self.pos + (12, 12) + (self.font.size(self.text[:cursor_index])[0], 0)
        return cursor_pos

    def remove_selected(self) -> bool:
        if not self.selecting: return False
        self.text = cut_from_str(self.text, (self.left_cursor, self.right_cursor - 1))
        self.cursor_index = self.left_cursor
        self.selecting = False
        return True

    @lru_cache(1)
    def save_to_history(self, text: str) -> None:
        if self.text == self.undo_history[-1][0]: return
        self.undo_history.append((self.text, self.cursor_index))
        self.redo_history.clear()

    def draw_selection_box(self, pos_begin: VEC, pos_end: VEC) -> None:
        rect = pygame.Rect(pos_begin, (pos_end.x - pos_begin.x, self.text_height - 18))
        trans_surf = pygame.Surface(rect.size, SRCALPHA)
        trans_surf.fill((0, 120, 215, 50))

        self.manager.screen.blit(trans_surf, rect)
        pygame.draw.rect(self.manager.screen, (0, 120, 215), rect, 1)

    def draw_selection(self) -> None:
        pos_begin = self.calc_cursor_pos(self.left_cursor)
        pos_end = self.calc_cursor_pos(self.right_cursor)

        if pos_end.y == pos_begin.y:
            self.draw_selection_box(pos_begin, pos_end)

    def draw(self) -> None:
        self.manager.screen.blit(FONT[50].render(self.text, False, (0, 0, 0)), self.pos + (12, 0))

        if self.selecting:
            self.draw_selection()

        if self.cursor_visible:
            pygame.draw.line(self.manager.screen, (0, 0, 0), self.cursor_pos, self.cursor_pos + (0, self.text_height - 18), 1)