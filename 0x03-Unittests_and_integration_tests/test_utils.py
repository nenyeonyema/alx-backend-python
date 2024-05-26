#!/usr/bin/env python3
""" Unittesting """
import unittest
from parameterized import parameterized
from utils import access_nested_map
from unittest.mock import patch, Mock, PropertyMock
from utils import get_json, memoize
from client import GithubOrgClient
import fixtures


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

    def test_public_repos_url(self):
        with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
            test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
            mock_org.return_value = test_payload

            client = GithubOrgClient("google")
            result = client._public_repos_url

            self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """ Test pub reops """
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url', new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://api.github.com/orgs/google/repos"

            client = GithubOrgClient("google")
            result = client.public_repos()

            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/google/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """ Test license """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


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


@parameterized_class([
    {"org_payload": fixtures.org_payload,
     "repos_payload": fixtures.repos_payload,
     "expected_repos": fixtures.expected_repos,
     "apache2_repos": fixtures.apache2_repos}
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up class method to mock requests.get"""
        cls.get_patcher = patch('requests.get', autospec=True)

        # Start patcher
        cls.mock_get = cls.get_patcher.start()

        # Setup side_effect
        def get_json_side_effect(url):
            if url == "https://api.github.com/orgs/google":
                return Mock(json=lambda: cls.org_payload)
            elif url == "https://api.github.com/orgs/google/repos":
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})

        cls.mock_get.side_effect = get_json_side_effect

        @classmethod
    def tearDownClass(cls):
        """Tear down class method to stop the patcher"""
        cls.get_patcher.stop()

    @parameterized.expand([
        (fixtures.expected_repos,),
    ])
    def test_public_repos(self, expected_repos):
        """Test public_repos method"""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, expected_repos)

    @parameterized.expand([
        (fixtures.apache2_repos,),
    ])
    def test_public_repos_with_license(self, expected_repos):
        """Test public_repos method with license"""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, expected_repos)


if __name__ == '__main__':
    unittest.main()
