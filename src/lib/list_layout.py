def python_sidebar(python_input):
    """
    Create the `Layout` for the sidebar with the configurable options.
    """

    def get_text_fragments():
        tokens = []

        def append_category(category):
            tokens.extend(
                [
                    ("class:sidebar", "  "),
                    ("class:sidebar.title", "   %-36s" % category.title),
                    ("class:sidebar", "\n"),
                ]
            )

        def append(index: int, label: str, status: str):
            selected = index == python_input.selected_option_index

            @if_mousedown
            def select_item(mouse_event: MouseEvent) -> None:
                python_input.selected_option_index = index

            @if_mousedown
            def goto_next(mouse_event: MouseEvent) -> None:
                " Select item and go to next value. "
                python_input.selected_option_index = index
                option = python_input.selected_option
                option.activate_next()

            sel = ",selected" if selected else ""

            tokens.append(("class:sidebar" + sel, " >" if selected else "  "))
            tokens.append(("class:sidebar.label" + sel, "%-24s" % label, select_item))
            tokens.append(("class:sidebar.status" + sel, " ", select_item))
            tokens.append(("class:sidebar.status" + sel, "%s" % status, goto_next))

            if selected:
                tokens.append(("[SetCursorPosition]", ""))

            tokens.append(
                ("class:sidebar.status" + sel, " " * (13 - len(status)), goto_next)
            )
            tokens.append(("class:sidebar", "<" if selected else ""))
            tokens.append(("class:sidebar", "\n"))

        i = 0
        for category in python_input.options:
            append_category(category)

            for option in category.options:
                append(i, option.title, "%s" % option.get_current_value())
                i += 1

        tokens.pop()  # Remove last newline.

        return tokens

    class Control(FormattedTextControl):
        def move_cursor_down(self):
            python_input.selected_option_index += 1

        def move_cursor_up(self):
            python_input.selected_option_index -= 1

    return Window(
        Control(get_text_fragments),
        style="class:sidebar",
        width=Dimension.exact(43),
        height=Dimension(min=3),
        scroll_offsets=ScrollOffsets(top=1, bottom=1),
    )
