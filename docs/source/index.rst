.. created by sphinxter
.. default-domain:: py

yaes
====

.. toctree::
    :maxdepth: 1
    :glob:
    :hidden:

    self
    *

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

.. class:: Engine(env=None)

    Class for expanding complex data (YAML / JSON) with Jinja2 templating

    :param env: optional jinja2 Environment to use with transform
    :type env: jinja2.Environment

    .. attribute:: env
        :type: jinja2.Environment

        Jinja2 environment

    .. method:: condition(block: dict, values: dict) -> bool

        Evaludates condition in values

        It's best to use '{?' and '?}' as conditions with straight Jinja2 with '{{' and '}}' will be deprecated.

        :param block: block to evaulate
        :type block: dict
        :param values: values to evaluate with
        :type values: dict
        :return: The evaluated condition
        :rtype: bool

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

            engine.condition({}, {})
            # True

            block = {
                "condition": "{{ a == 1 }}"
            }

            engine.condition(block, {"a": 1})
            # True

            engine.condition(block, {"a": 2})
            # False

            block = {
                "condition": "{? a == 1 ?}"
            }

            engine.condition(block, {"a": 1})
            # True

            engine.condition(block, {"a": 2})
            # False

    .. method:: each(blocks, values: dict)

        Go through blocks, iterating and checking conditions, yield blocks that pass

        :param blocks: blocks to evaulate
        :type blocks: dict or list
        :param values: values to evaluate with
        :type values: dict
        :return: Passing blocks
        :rtype: Iterator

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

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

            list(engine.each(block, values))
            # [
            #     (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": 7}),
            #     (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": 7}),
            #     (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": 7})
            # ]

    .. method:: iterate(block: dict, values: dict) -> list

        Iterates values with transposition

        :param block: block to evaulate
        :type block: dict
        :param values: values to evaluate with
        :type values: dict
        :return: The list of blocks iterated
        :rtype: list

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

            values = {
                "a": 1,
                "cs": [2, 3],
                "ds": "nuts"
            }

            engine.iterate({}, values)
            # [{}]

            block = {
                "transpose": {
                    "b": "a"
                },
                "iterate": {
                    "c": "cs",
                    "d": "ds"
                }
            }

            engine.iterate(block, values)
            # [
            #     {
            #         "b": 1,
            #         "c": 2,
            #         "d": "n"
            #     },
            #     {
            #         "b": 1,
            #         "c": 2,
            #         "d": "u"
            #     },
            #     {
            #         "b": 1,
            #         "c": 2,
            #         "d": "t"
            #     },
            #     {
            #         "b": 1,
            #         "c": 2,
            #         "d": "s"
            #     },
            #     {
            #         "b": 1,
            #         "c": 3,
            #         "d": "n"
            #     },
            #     {
            #         "b": 1,
            #         "c": 3,
            #         "d": "u"
            #     },
            #     {
            #         "b": 1,
            #         "c": 3,
            #         "d": "t"
            #     },
            #     {
            #         "b": 1,
            #         "c": 3,
            #         "d": "s"
            #     }
            # ]

    .. method:: transform(template, values: dict)

        Renders a Jinja2 template using values sent

        If the template is a str and is enclosed by '{?' and '?}', it will render the template but evaluate as a bool.

        If the template is a str and is enclosed by '{[' and ']}', it will lookup the value in valuue using overscore notation.

        Else if the tempalte is a str, it will render the template in the standard Jinja2 way.

        If the template is a list, it will recurse and render each item.

        If the template is a dict, it will recurse each key and render each item.

        Else return the template as is.

        :param template: template to use
        :type template: bool or str or list or dict
        :param values: values to use with the template
        :type values: dict
        :return: The rendered value

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

            engine.transform("{{ a }}", {"a": 1})
            # '1'

            engine.transform(["{{ a }}"], {"a": 1})
            # ['1']

            engine.transform({"b": "{{ a }}"}, {"a": 1})
            # {"b": '1'}

            engine.transform("{{ a == 1 }}", {"a": 1})
            # 'True'

            engine.transform("{{ a != 1 }}", {"a": 1})
            # 'False'

            engine.transform(True, {})
            # True

            engine.transform(False, {})
            # False

            engine.transform("{? 1 == 1 ?}", {})
            # True

            engine.transform("{? 1 == 0 ?}", {})
            # False

            engine.transform("{[ a__b ]}", {})
            # None

            engine.transform("{[ a__b ]}", {"a": {"b": 3}})
            # 3

    .. staticmethod:: transpose(block: dict, values: dict) -> dict

        Transposes values, allows for the same value under a different name

        :param block: block to evaulate
        :type block: dict
        :param values: values to evaluate with
        :type values: dict
        :return: The new values block transposed
        :rtype: dict

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

            engine.transpose({"transpose": {"b": "a"}}, {"a": 1})
            # {"b": 1}
