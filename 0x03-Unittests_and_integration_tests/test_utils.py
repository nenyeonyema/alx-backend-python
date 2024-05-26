#!/usr/bin/env python3
""" Unittesting """
import unittest
from parameterized import parameterized
from utils import access_nested_map
from unittest.mock import patch, Mock
from utils import get_json


class TestAccessNestedMap(unittest.TestCase):
    """ Parameterized tests """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])

    def test_access_nested_map(self, nested_map, path, expected_result):
        """ Test the nested map function """
        self.assertEqual(access_nested_map(nested_map, path), expected_result)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])

    def test_access_nested_map_exception(self, nested_map, path):
        """ Test for keyError """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), repr(path[-1]))

    @patch('utils.requests.get')
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])

    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Set up the mock to return a response with
        the test_payload as its JSON data
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function and check the result
        result = get_json(test_url)
        self.assertEqual(result, test_payload)

        # Ensure the mock was called exactly once with the test_url
        mock_get.assert_called_once_with(test_url)


if __name__ == '__main__':
    unittest.main()
