"""Offline validation tests; no SDK or phone required."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_apk import load_config, validate_config


class MappingValidationTests(unittest.TestCase):
    def setUp(self):
        self.apps = [{'id': 'example-app', 'name': 'Example', 'package': 'com.example.app'}]
        self.fixes = [{'component': 'com.example.app/org.vendor.Launcher$Alias',
                       'drawable': 'min_example_app', 'source': 'device launcher query'}]
        self.names = {'min_example_app', 'legacy'}

    def check(self):
        validate_config(self.apps, self.fixes, self.names)

    def test_valid_alias_in_other_namespace(self):
        self.check()

    def test_checked_in_configuration(self):
        load_config()

    def test_bad_entries(self):
        original = copy.deepcopy(self.fixes)
        for field, value in [('component', 'com.example.app/.Launcher'),
                             ('component', 'ComponentInfo{com.example.app/com.example.Main}'),
                             ('drawable', 'missing'), ('drawable', 'legacy'),
                             ('source', ''), ('source', 123)]:
            with self.subTest(field=field, value=value):
                self.fixes = copy.deepcopy(original)
                self.fixes[0][field] = value
                with self.assertRaises(ValueError):
                    self.check()

    def test_duplicate_component(self):
        self.fixes *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate component'):
            self.check()

    def test_missing_coverage(self):
        self.fixes = []
        with self.assertRaisesRegex(ValueError, 'missing launcher'):
            self.check()

    def test_duplicate_app(self):
        self.apps *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate id or package'):
            self.check()

    def test_schema(self):
        for fixes in ({}, [None], [{'component': 'x'}], [dict(self.fixes[0], typo='x')]):
            with self.subTest(fixes=fixes), self.assertRaises(ValueError):
                validate_config(self.apps, fixes, self.names)
