# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
# pylint: disable=R0801
"""Test Index Lambda function."""

# python stuff
import os
import sys
import unittest


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
from rekognition_api.tests.test_setup import get_test_file  # noqa: E402


# from rekognition_api.lambda_index import lambda_handler  # noqa: E402


class TestLambdaIndex(unittest.TestCase):
    """Test Index Lambda function."""

    # load a mock lambda_index event
    event = get_test_file("json/apigateway_index_lambda_event.json")
    response = get_test_file("json/apigateway_index_lambda_response.json")

    def setUp(self):
        """Set up test fixtures."""

    def test_noop(self):
        """Test to ensure that test suite setup works and that lambda_handler is importable."""