yaes
====

Yet Another Expansion Syntax (pronounced 'Yasssss Kweeeeen') for expanding complex data (YAML / JSON) with Jinja2 templating::

    import yaes

    values = {
        "a": 1,
        "cs": [2, 3],
        "ds": "nuts"
    }

    block = {
        "transpose": {
            "b": "a"
        },
        "iterate": {
            "c": "cs",
            "d": "ds"
        },
        "condition": "{{ c != 3 and d != 't' }}",
        "values": {"L": 7}
    }

    list(yaes.each(block, values))
    # [
    #     (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": 7}),
    #     (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": 7}),
    #     (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": 7})
    # ]
