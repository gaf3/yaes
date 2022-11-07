import unittest
import sphinxter.unittest

import yaes


class TestEngine(sphinxter.unittest.TestCase):

    def setUp(self):

        self.engine = yaes.Engine()

    def test___init__(self):

        init = yaes.Engine("yep")

        self.assertEqual(init.env, "yep")

    def test_transform(self):

        self.assertEqual('1', self.engine.transform("{{ a }}", {"a": 1}))
        self.assertEqual(['1'], self.engine.transform(["{{ a }}"], {"a": 1}))
        self.assertEqual({"b": '1'}, self.engine.transform({"b": "{{ a }}"}, {"a": 1}))
        self.assertEqual('True', self.engine.transform("{{ a == 1 }}", {"a": 1}))
        self.assertEqual('False', self.engine.transform("{{ a != 1 }}", {"a": 1}))
        self.assertEqual(True, self.engine.transform(True, {}))
        self.assertEqual(False, self.engine.transform(False, {}))
        self.assertEqual(True, self.engine.transform("{? 1 == 1 ?}", {}))
        self.assertEqual(False, self.engine.transform("{? 1 == 0 ?}", {}))
        self.assertEqual(None, self.engine.transform("{[ a__b ]}", {}))
        self.assertEqual(3, self.engine.transform("{[ a__b ]}", {"a": {"b": 3}}))

        self.assertSphinxter(yaes.Engine.transform)

    def test_require(self):

        self.assertTrue(self.engine.require({}, {}))

        block = {
            "require": "a"
        }

        self.assertTrue(self.engine.require(block, {"a": 1}))
        self.assertFalse(self.engine.require(block, {}))

        block = {
            "require": ["a__b", "{[ a__b ]}"]
        }

        self.assertFalse(self.engine.require(block, {}))
        self.assertFalse(self.engine.require(block, {"a": {"b": "c"}}))
        self.assertTrue(self.engine.require(block, {"a": {"b": "c"}, "c": "yep"}))

        self.assertSphinxter(yaes.Engine.require)

    def test_transpose(self):

        self.assertEqual({"b": 1}, self.engine.transpose({"transpose": {"b": "a"}}, {"a": 1}))

        self.assertSphinxter(yaes.Engine.transpose)

    def test_iterate(self):

        values = {
            "a": 1,
            "cs": [2, 3],
            "ds": "nuts"
        }

        self.assertEqual(self.engine.iterate({}, values), [{}])

        block = {
            "transpose": {
                "b": "a"
            },
            "iterate": {
                "c": "cs",
                "d": "ds"
            }
        }

        self.assertEqual(self.engine.iterate(block, values), [
            {"b": 1, "c": 2, "d": "n"},
            {"b": 1, "c": 2, "d": "u"},
            {"b": 1, "c": 2, "d": "t"},
            {"b": 1, "c": 2, "d": "s"},
            {"b": 1, "c": 3, "d": "n"},
            {"b": 1, "c": 3, "d": "u"},
            {"b": 1, "c": 3, "d": "t"},
            {"b": 1, "c": 3, "d": "s"}
        ])

        self.assertSphinxter(yaes.Engine.iterate)

    def test_condition(self):

        self.assertTrue(self.engine.condition({}, {}))

        block = {
            "condition": "{{ a == 1 }}"
        }

        self.assertTrue(self.engine.condition(block, {"a": 1}))
        self.assertFalse(self.engine.condition(block, {"a": 2}))

        block = {
            "condition": "{? a == 1 ?}"
        }

        self.assertTrue(self.engine.condition(block, {"a": 1}))
        self.assertFalse(self.engine.condition(block, {"a": 2}))

        self.assertSphinxter(yaes.Engine.condition)

    def test_each(self):

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

        self.assertEqual(list(self.engine.each(block, values)), [
            (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": 7}),
            (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": 7}),
            (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": 7})
        ])

        block = {
            "require": "a",
        }

        self.assertEqual(list(self.engine.each(block, {})), [])

        self.assertSphinxter(yaes.Engine.each)

class TestYeas(sphinxter.unittest.TestCase):

    def test_each(self):

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

        self.assertEqual(list(yaes.each(block, values)), [
            (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "n", "L": 7}),
            (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "u", "L": 7}),
            (block, {"a": 1, "cs": [2, 3], "ds": "nuts", "b": 1, "c": 2, "d": "s", "L": 7})
        ])

        self.assertSphinxter(yaes.each)
