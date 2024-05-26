#!/usr/bin/env python3
""" Unittesting """
import unittest
from parameterized import parameterized
from utils import access_nested_map
from unittest.mock import patch, Mock, PropertyMock
from utils import get_json, memoize
from client import GithubOrgClient


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

class TestGetJson(unittest.TestCase):
    """ Test Get JSON """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Set up the mock to return a response with
        the test_payload as its JSON data
        """
        # Set up the mock to return a response with the test_payload as its JSON data
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function and check the result
        result = get_json(test_url)
        self.assertEqual(result, test_payload)

        # Ensure the mock was called exactly once with the test_url
        mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """ Test Memoize """
    def test_memoize(self):
        """ Test Memoize """
        class TestClass:
            "Test class """
            def a_method(self):
                """ a_method """
                return 42

            @memoize
            def a_property(self):
                """ a_property """
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            obj = TestClass()
            
            # Call a_property twice
            result1 = obj.a_property
            result2 = obj.a_property
            
            # Check that a_method was only called once
            mock_method.assert_called_once()
            
            # Check that the results are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)


class TestGithubOrgClient(unittest.TestCase):
    """ TestGithubOrgClient """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """ Test Org """
        test_payload = {"payload": True}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, test_payload)


if __name__ == '__main__':
    unittest.main()
