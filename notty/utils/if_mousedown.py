from typing import Callable, TypeVar, cast
from prompt_toolkit.mouse_events import MouseEvent, MouseEventType

_T = TypeVar("_T", bound=Callable[[MouseEvent], None])

def if_mousedown(handler: _T) -> _T:
    """
    Decorator for mouse handlers.
    Only handle event when the user pressed mouse down.
    (When applied to a token list. Scroll events will bubble up and are handled
    by the Window.)
    """

    def handle_if_mouse_down(mouse_event: MouseEvent):
        if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
            return handler(mouse_event)
        else:
            return NotImplemented

    return cast(_T, handle_if_mouse_down)