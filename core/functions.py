def check_attribute(key, val):
    """Return a check function which returns True when <obj> attribute <key> value is equal to <val>"""

    def function(obj):
        return getattr(obj, key) == val

    return function
