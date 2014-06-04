import sys
import os

# parent folder holds libraries which needs to be included
sys.path.append(os.path.realpath('..'))

import simplejson as json
from simplejson import OrderedDict

import decimal
import unittest


class TestIssues(unittest.TestCase):
    def setUp(self):
        pass

    def test_ascii_issue_10(self):
        tmp_str = '{"tempstr":"\u2022"}'
        expected_output = '''{
  "tempstr": "\\u2022"
}'''
        obj = json.loads(tmp_str, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal)
        tmp_str = json.dumps(obj, indent=2, ensure_ascii=True, sort_keys=False,
                             separators=(',', ': '),
                             use_decimal=True)
        self.assertEqual(tmp_str, expected_output)

    # issue 15
    def test_float_issue_15(self):
        tmp_str = '{"real":0.99}'
        expected_output = """{
  "real": 0.99
}"""
        obj = json.loads(tmp_str, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal)
        tmp_str = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False,
                             separators=(',', ': '),
                             use_decimal=True)
        self.assertEqual(tmp_str, expected_output)

    # issue 16
    def test_float_issue_16_1(self):
        tmp_str = '{ "float": 1.0 }'
        obj = json.loads(tmp_str, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal)
        self.assertEqual(obj['float'], 1.0)
        tmp_str = json.dumps(obj, indent=0, ensure_ascii=False, sort_keys=False,
                             separators=(',', ': '),
                             use_decimal=True)
        self.assertEqual(tmp_str.split('\n')[1], '"float": 1.0')

    # issue 16
    def test_float_issue_16_2(self):
        tmp_str = '{"test1":0.99, "test2":"1.99", "test3":1.00000000001, "test4":1.99, "test5":1,' \
                  ' "test6":4.589999999999999999, "test7":1.0}'
        expected_output = """{
  "test1": 0.99,
  "test2": "1.99",
  "test3": 1.00000000001,
  "test4": 1.99,
  "test5": 1,
  "test6": 4.589999999999999999,
  "test7": 1.0
}"""
        obj = json.loads(tmp_str, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal)
        tmp_str = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False,
                             separators=(',', ': '),
                             use_decimal=True)
        self.assertEqual(tmp_str, expected_output)

    def test_compress_feature(self):
        tmp_str = """{
  "real": 0.99
}"""
        expected_output = '{"real":0.99}'
        obj = json.loads(tmp_str, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal)
        tmp_str = json.dumps(obj, ensure_ascii=False, sort_keys=False,
                             separators=(',', ':'),
                             use_decimal=True)
        self.assertEqual(tmp_str, expected_output)


if __name__ == '__main__':
    unittest.main()
