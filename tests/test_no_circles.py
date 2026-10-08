"""No two callbacks may wake each other in a circle (A changes what wakes B, and
B changes what wakes A). Dash shows a "Circular Dependencies" error in the
browser for that. A Settings switch reads its saved value as a State instead
(see show_color_setting and show_reminders_setting).

Allowed, and not counted: a callback that changes its own inputs (Dash allows
that), and outputs marked allow_duplicate (Dash doesn't check those)."""


def callback_links():
    """For each callback: the callbacks it wakes up through its outputs."""
    import dash._callback as dash_callbacks
    import trade.app  # noqa: F401  (registers every callback of the app)

    callbacks = dash_callbacks.GLOBAL_CALLBACK_LIST
    outputs = [{o for o in c["output"].strip(".").split("...") if o and "@" not in o} for c in callbacks]
    inputs = [{f"{i['id']}.{i['property']}" for i in c["inputs"] if isinstance(i["id"], str)} for c in callbacks]
    return {a: {b for b in range(len(callbacks)) if b != a and outputs[a] & inputs[b]} for a in range(len(callbacks))}, callbacks


def find_circle(links):
    state = {}

    def visit(node, path):
        state[node] = "open"
        for nxt in links[node]:
            if state.get(nxt) == "open":
                return path[path.index(nxt):] + [nxt]
            if nxt not in state:
                found = visit(nxt, path + [nxt])
                if found:
                    return found
        state[node] = "done"
        return None

    for start in links:
        if start not in state:
            found = visit(start, [start])
            if found:
                return found
    return None


def test_no_two_callbacks_wake_each_other_in_a_circle():
    links, callbacks = callback_links()
    circle = find_circle(links)
    assert circle is None, "Callbacks in a circle: " + "  ->  ".join(callbacks[i]["output"][:60] for i in circle)


def test_dark_mode_switch_shows_and_saves_the_setting():
    import trade.callbacks.settings.advanced as advanced
    assert advanced.show_color_setting("advanced", False) is False
    assert advanced.show_color_setting("advanced", None) is True          # default: on
    assert advanced.save_color_setting(False) is False
    assert advanced.save_color_setting(True) is True
