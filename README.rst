yaes
====

.. module:: yaes

Yet Another Expansion Syntax (pronounced "Yasssss Kweeeeen") for expanding complex data (YAML / JSON) with Jinja2 templating

.. function:: each(blocks, values: dict, env=None)

    Short hand each function for basic usage

    Go through blocks, iterating and checking conditions, yield blocks that pass

    :param blocks: blocks to evaulate
    :type blocks: dict or list
    :param values: values to evaluate with
    :type values: dict
    :param env: optional Jinja2.Environment to use for transformations
    :type env: Jinja2.Environment
    :return: Passing blocks
    :rtype: Iterator

    **Usage**

    ::

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
