"""
description: |
    Yet Another Expansion Syntax (pronounced 'Yasssss Kweeeeen') for expanding complex data (YAML / JSON) with Jinja2 templating
"""

# pylint: disable=consider-using-f-string

import copy
import jinja2
import overscore


class Engine:
    """
    Class for expanding complex data (YAML / JSON) with Jinja2 templating
    """

    env = None  # Jinja2 environment
    "type: jinja2.Environment"

    def __init__(self,
        env=None    # optional jinja2 Environment to use with transform
    ):
        """
        parameters:
            env:
                type: jinja2.Environment
        """

        self.env = env if env else jinja2.Environment()

    def transform(self,
        template,   # template to use
        values:dict # values to use with the template
    ):
        """
        description: |
            Renders a Jinja2 template using values sent

            If the template is a str and is enclosed by '{?' and '?}', it will render the template but evaluate as a bool.

            If the template is a str and is enclosed by '{[' and ']}', it will lookup the value in valuue using overscore notation.

            Else if the tempalte is a str, it will render the template in the standard Jinja2 way.

            If the template is a list, it will recurse and render each item.

            If the template is a dict, it will recurse each key and render each item.

            Else return the template as is.
        parameters:
            template:
                type:
                - bool
                - str
                - list
                - dict
        return: The rendered value
        usage: |
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
        """

        if isinstance(template, str):
            if len(template) > 4 and template[:2] == "{?" and template[-2:] == "?}":
                return self.env.from_string("{{%s}}" % template[2:-3]).render(**values) == "True"
            if len(template) > 4 and template[:2] == "{[" and template[-2:] == "]}":
                return overscore.get(values, template[2:-3].strip())
            return self.env.from_string(template).render(**values)
        if isinstance(template, list):
            return [self.transform(item, values) for item in template]
        if isinstance(template, dict):
            return {key: self.transform(item, values) for key, item in template.items()}

        return template

    def require(self,
        block:dict, # block to evaulate
        values:dict # values to evaluate with
    )->bool:
        """
        description: |
            Determines whether values are set to process a block
        usage: |
            ::

                import yaes

                engine = yaes.Engine()

                engine.require({}, {})
                # True

                block = {
                    "require": "a"
                }

                engine.require(block, {"a": 1})
                # True

                engine.require(block, {})
                # False

                block = {
                    "require": ["a__b", "{[ a__b ]}"]
                }

                engine.require(block, {})
                # False

                engine.require(block, {"a": {"b": "c"}})
                # False

                engine.require(block, {"a": {"b": "c"}, "c": "yep"})
                # True
        """

        if "require" not in block:
            return True

        require = block["require"]

        if not isinstance(require, list):
            require = [require]

        for path in require:
            if not overscore.has(values, self.transform(path, values)):
                return False

        return True

    @staticmethod
    def transpose(
        block:dict, # block to evaulate
        values:dict # values to evaluate with
    )->dict:
        """
        description: Transposes values, allows for the same value under a different name
        usage: |
            ::

                import yaes

                engine = yaes.Engine()

                engine.transpose({"transpose": {"b": "a"}}, {"a": 1})
                # {"b": 1}
        return: The new values block transposed
        """

        transpose = block.get("transpose", {})

        return {derivative: values[original] for derivative, original in transpose.items() if original in values}

    def iterate(self,
        block:dict, # block to evaulate
        values:dict # values to evaluate with
    )->list:
        """
        description: Iterates values with transposition
        return: The list of blocks iterated
        usage: |
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
        """

        iterate_values = [self.transpose(block, values)]

        iterate = block.get("iterate", {})

        for one in sorted(iterate.keys()):
            many_values = []
            for many_value in iterate_values:
                for value in values[iterate[one]]:
                    many_values.append({**many_value, one: value})
            iterate_values = many_values

        return iterate_values

    def condition(self,
        block:dict, # block to evaulate
        values:dict # values to evaluate with
    )->bool:
        """
        description: |
            Evaludates condition in values

            It's best to use '{?' and '?}' as conditions with straight Jinja2 with '{{' and '}}' will be deprecated.
        return: The evaluated condition
        usage: |
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
        """

        if "condition" not in block:
            return True

        value = self.transform(block["condition"], values)

        if isinstance(value, bool):
            return value

        return value == "True"

    def each(self,
        blocks,     # blocks to evaulate
        values:dict # values to evaluate with
    ):
        """
        description: Go through blocks, iterating and checking conditions, yield blocks that pass
        parameters:
            blocks:
                type:
                - dict
                - list
        return:
            description: Passing blocks
            type: Iterator
        usage: |
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

                block = {
                    "require": "a",
                }

                list(engine.each(block, {}))
                # []
        """

        if isinstance(blocks, dict):
            blocks = [blocks]

        for block in blocks:

            if not self.require(block, values):
                continue

            for iterate_values in self.iterate(block, values):
                block_values = {**values, **iterate_values, **block.get("values", {})}
                if self.condition(block, block_values):
                    yield copy.deepcopy(block), block_values

def each(
    blocks,         # blocks to evaulate
    values:dict,    # values to evaluate with
    env=None        # optional Jinja2.Environment to use for transformations
):
    """
    description: |
        Short hand each function for basic usage

        Go through blocks, iterating and checking conditions, yield blocks that pass
    parameters:
        blocks:
            type:
            - dict
            - list
        env:
            type: Jinja2.Environment
    return:
        description: Passing blocks
        type: Iterator
    usage: |
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

            block = {
                "require": "a",
            }

            list(yaes.each(block, {}))
            # []
    """

    for block in Engine(env).each(blocks, values):
        yield block
