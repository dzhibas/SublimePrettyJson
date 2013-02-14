import json
import simplejson as json
from simplejson import OrderedDict
import decimal
import unittest


class TestFloatConversion(unittest.TestCase):

    def setUp(self):
        pass

    def test_float(self):
        tmp_str = '{ "float": 1.0 }'
        obj = json.loads(tmp_str, object_pairs_hook=OrderedDict, parse_float=decimal.Decimal)
        self.assertEqual(obj['float'], 1.0)
        tmp_str = json.dumps(obj, indent=0, ensure_ascii=False, sort_keys=False,
                    separators=(',', ': '),
                    use_decimal=True)
        self.assertEqual(tmp_str.split('\n')[1], u'"float": 1.0')


if __name__ == '__main__':
    unittest.main()
