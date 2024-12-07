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

Yet Another Expansion Syntax (pronounced 'Yasssss Kweeeeen') for expanding complex data (YAML / JSON) with Jinja2 templating

If a block has no control keywords, everything is emitted as is::

    import yaes

    block = {
        "ya": "{{ a }}"
    }

    values = {
        "a": "sure"
    }

    list(yaes.each(block, values))
    # [
    #     ({"ya": "{{ a }}"}, {"a": "sure"})
    # ]

The behavior is the same if you send a list of blocks::

    list(yaes.each([block], values))
    # [
    #     ({"ya": "{{ a }}"}, {"a": "sure"})
    # ]

requires
--------

If a requires keyword is present, all the keys listed must be in values for the block to emitted::

    blocks = [
        {
            "name": "one",
            "requires": "a"
        },
        {
            "name": "twp",
            "requires": ["a", "b"]
        }
    ]

    values = {
        "a": "sure"
    }

    list(yaes.each(blocks, values))
    # [
    #     ({"name": "one"}, {"a": "sure"})
    # ]

.. note::

    requires can be a str or list of str.

This is useful for modules like opengui, where we don't want to evaluate the conditions on some fields
unless other fields in those conditions actually have values.

transpose
---------

If a transpose keyword is present, it'll use the key pairs to transpose the values::

    blocks = [
        {
            "name": "one",
            "transpose": {
                "b": "a"
            }
        }
    ]

    values = {
        "a": "sure"
    }

    list(yaes.each(blocks, values))
    # [
    #     ({"name": "one"}, {"a": "sure", "b": "sure"})
    # ]

.. note::

    you can have multiple values to transpose

This is useful if you're re-using a template that uses veriables and you want to replace
them with your usage's specific variables.

iterate
-------

If a iterate keyword is present, it'll use the key pairs to iterate new values::

    blocks = [
        {
            "name": "{{ fruit }}",
            "iterate": {
                "fruit": "fruits"
            }
        }
    ]

    values = {
        "fruits": [
            "apple",
            "pear",
            "orange"
        ]
    }

    list(yaes.each(blocks, values))
    # [
    #     (
    #         {
    #             "name": "{{ fruit }}"
    #         },
    #         {
    #             "fruit": "apple",
    #             "fruits": [
    #                 "apple",
    #                 "pear",
    #                 "orange"
    #             ]
    #         }
    #     ),
    #     (
    #         {
    #             "name": "{{ fruit }}"
    #         },
    #         {
    #             "fruit": "pear",
    #             "fruits": [
    #                 "apple",
    #                 "pear",
    #                 "orange"
    #             ]
    #         }
    #     ),
    #     (
    #         {
    #             "name": "{{ fruit }}"
    #         },
    #         {
    #             "fruit": "orange",
    #             "fruits": [
    #                 "apple",
    #                 "pear",
    #                 "orange"
    #             ]
    #         }
    #     )
    # ]

.. note::

    you can have multiple values to iterate, and it'll iterate over the different
    pairs alphabetically by key

This is useful with opengui as you can take the values of a multi option field and
use those values to create a new field for each option selected.

condition
---------

If a condition keyword is present, it'll only emit the block if the condition evaluates True::

    blocks = [
        {
            "name": "one",
            "condition": "{? a == 1 ?}"
        },
        {
            "name": "two",
            "condition": "{? a == 2 ?}"
        }
    ]

    values = {
        "a": 1
    }

    list(yaes.each(blocks, values))
    # [
    #     ({"name": "one"}, {"a": 1})
    # ]

.. note::

    make sure you use '{?' and '?}' in the condition so it renders as a boolean.

This is useful if you only want to use a block under certain conditions.

blocks
------

If a blocks keyword is present, it'll expand those blocks, using the parent block as a base::

    blocks = [
        {
            "base": "value",
            "blocks": [
                {
                    "name": "one"
                },
                {
                    "name": "two",
                    "base": "override"
                }
            ]
        }
    ]

    values = {
        "a": 1
    }

    list(yaes.each(blocks, values))
    # [
    #     (
    #         {
    #             "base": "value",
    #             "name": "one"
    #         },
    #         {
    #             "a": 1
    #         }
    #     ),
    #     (
    #         {
    #             "base": "override",
    #             "name": "two"
    #         },
    #         {
    #             "a": 1
    #         }
    #     )
    # ]

.. note::

    blocks within blocks with control keywords will have those keywords evaluated

This is useful if you have a condition or iterate that you want to apply to multiple
block without having to use those keywords on each block.

values
------

If a values keyword is present, it'll merge those values into the values emitted::

    blocks = [
        {
            "name": "one"
        },
        {
            "name": "two",
            "values": {
                "a": 2,
                "c": "{{ b }}sah"
            }
        }
    ]

    values = {
        "a": 1,
        "b": "yes"
    }

    list(yaes.each(blocks, values))
    # [
    #     (
    #         {
    #             "name": "one"
    #         },
    #         {
    #             "a": 1,
    #             "b": "yes"
    #         }
    #     ),
    #     (
    #         {
    #             "name": "two"
    #         },
    #         {
    #             "a": 2,
    #             "b": "yes",
    #             "c": "yessah"
    #         }
    #     )
    # ]

.. note::

    you can have multiple pairs in values

This is useful if you want to override the existing values but at this point I don't
think even I've ever used it.

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
            "ya": "sure",
            "transpose": {
                "b": "a"
            },
            "iterate": {
                "c": "cs",
                "d": "ds"
            },
            "condition": "{{ c != 3 and d != 't' }}",
            "values": {"L": "{{ c + 5 }}"},
            "blocks": [
                {},
                {
                    "ya": "ofcourse",
                    "condition": "{{ d == 'u' }}",
                }
            ]
        }

        list(yaes.each(block, values))
        # [
        #     ({"ya": "sure"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": "7"}),
        #     ({"ya": "sure"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": "7"}),
        #     ({"ya": "ofcourse"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": "7"}),
        #     ({"ya": "sure"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": "7"})
        # ]

        block = {
            "requires": "a",
        }

        list(yaes.each(block, {}))
        # []

.. class:: Engine(env=None)

    Class for expanding complex data (YAML / JSON) with Jinja2 templating

    :param env: optional jinja2 Environment to use with transform
    :type env: jinja2.Environment

    .. attribute:: CONTROLS

        list of control keywords

    .. attribute:: env
        :type: jinja2.Environment

        Jinja2 environment

    .. method:: blocks(block: dict, values: dict)

        :param block: block to evaulate
        :type block: dict
        :param values: values to evaluate with
        :type values: dict
        :return: Merged (child on top of parent) blocks
        :rtype: Iterator

        **Usage**

        If just a regular block, returns a cleaned copy::

            import yaes

            engine = yaes.Engine()

            block = {
                "ya": "sure",
                "requires": "a",
                "transpose": {
                    "b": "a"
                },
                "iterate": {
                    "c": "cs",
                    "d": "ds"
                },
                "condition": "{{ c != 3 and d != 't' }}",
                "values": {"L": "{{ c + 5 }}"}
            }

            list(engine.blocks(block, {}))
            # [({"ya": "sure"}, {})]

        If the block has blocks, it'll merge them onto top of the parent block after processing them::

            values = {
                "a": 1,
                "cs": [2, 3],
                "ds": "nuts"
            }

            block = {
                "ya": "sure",
                "blocks": [
                    {
                        "ya": "whatever"
                    },
                    {
                        "ya": "ofcourse",
                        "requires": "a",
                        "transpose": {
                            "b": "a"
                        },
                        "iterate": {
                            "c": "cs",
                            "d": "ds"
                        },
                        "condition": "{{ c != 3 and d != 't' }}",
                        "values": {"L": "{{ c + 5 }}"},
                    }
                ]
            }

            list(engine.blocks(block, values))
            # [
            #     ({"ya": "whatever"}, {"a": 1, "cs": [2, 3], "ds": "nuts"}),
            #     ({"ya": "ofcourse"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": "7"}),
            #     ({"ya": "ofcourse"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": "7"}),
            #     ({"ya": "ofcourse"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": "7"})
            # ]

    .. classmethod:: clean(block: dict) -> dict

        :param block: Block to clean
        :type block: dict
        :rtype: dict

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

            block = {
                "ya": "sure",
                "requires": "a",
                "transpose": {
                    "b": "a"
                },
                "iterate": {
                    "c": "cs",
                    "d": "ds"
                },
                "condition": "{{ c != 3 and d != 't' }}",
                "blocks": [1,2, 3],
                "values": {"L": 7}
            }

            engine.clean(block)
            # {"ya": "sure"}

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

        Iterate over block(s), expanding using control key words

        This is used for hihgly dynamic configurmation. Blacks are assumed to have JKinja2 templating and
        controls for conditions, loops, even whether a block can be evaluated. This determines what's ready
        and will expand blocks based on the control keywords sent.

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
                "ya": "sure",
                "transpose": {
                    "b": "a"
                },
                "iterate": {
                    "c": "cs",
                    "d": "ds"
                },
                "condition": "{{ c != 3 and d != 't' }}",
                "values": {"L": "{{ c + 5 }}"},
                "blocks": [
                    {},
                    {
                        "ya": "ofcourse",
                        "condition": "{{ d == 'u' }}",
                    }
                ]
            }

            list(engine.each(block, values))
            # [
            #     ({"ya": "sure"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": "7"}),
            #     ({"ya": "sure"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": "7"}),
            #     ({"ya": "ofcourse"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": "7"}),
            #     ({"ya": "sure"}, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": "7"})
            # ]

            block = {
                "requires": "a",
            }

            list(engine.each(block, {}))
            # []

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

    .. method:: requires(block: dict, values: dict) -> bool

        Determines whether values are set to process a block

        :param block: block to evaulate
        :type block: dict
        :param values: values to evaluate with
        :type values: dict
        :rtype: bool

        **Usage**

        ::

            import yaes

            engine = yaes.Engine()

            engine.requires({}, {})
            # True

            block = {
                "requires": "a"
            }

            engine.requires(block, {"a": 1})
            # True

            engine.requires(block, {})
            # False

            block = {
                "requires": ["a__b", "{[ a__b ]}"]
            }

            engine.requires(block, {})
            # False

            engine.requires(block, {"a": {"b": "c"}})
            # False

            engine.requires(block, {"a": {"b": "c"}, "c": "yep"})
            # True

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

            engine.transform("{[ a__b-c ]}", {"a": {"b-c": 3}})
            # 3

            engine.transform("{[ {{ first }}__{{ second }} ]}", {"first": "a", "second": "b-c", "a": {"b-c": 3}})
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
