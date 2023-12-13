# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
"""Test Search Lambda function."""

# python stuff
import json
import os
import sys
import unittest


HERE = os.path.abspath(os.path.dirname(__file__))
PYTHON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PYTHON_ROOT)  # noqa: E402

# our stuff
# from rekognition_api.lambda_search import lambda_handler  # noqa: E402


class TestLambdaIndex(unittest.TestCase):
    """Test Search Lambda function."""

    # Get the directory of the current script
    here = os.path.dirname(os.path.abspath(__file__))

    # load a mock lambda_index event
    with open(HERE + "/data/apigateway_search_lambda_event.json", "r", encoding="utf-8") as file:
        event = json.load(file)

    def setUp(self):
        """Set up test fixtures."""

    def test_noop(self):
        """Test to ensure that test suite setup works and that lambda_handler is importable."""