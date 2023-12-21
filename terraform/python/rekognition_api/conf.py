# -*- coding: utf-8 -*-
# pylint: disable=no-member
"""
Configuration for Lambda functions.

This module is used to configure the Lambda functions. It uses the pydantic_settings
library to validate the configuration values. The configuration values are read from
environment variables, or alternatively these can be set when instantiating Settings().

The configuration values are validated using pydantic. If the configuration values are
invalid, then a RekognitionConfigurationError is raised.

The configuration values are dumped to a dict using the dump property. This is used
to display the configuration values in the /info endpoint.

"""


import importlib.util

# python stuff
import json
import logging
import os  # library for interacting with the operating system
import platform  # library to view information about the server host this Lambda runs on
import re
from typing import Any, Dict, List, Optional

# 3rd party stuff
import boto3  # AWS SDK for Python https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
import pkg_resources
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from pydantic import Field, SecretStr, ValidationError, ValidationInfo, field_validator
from pydantic_settings import BaseSettings
from rekognition_api.const import HERE, IS_USING_TFVARS, TFVARS

# our stuff
from rekognition_api.exceptions import (
    RekognitionConfigurationError,
    RekognitionValueError,
)


logger = logging.getLogger(__name__)
TFVARS = TFVARS or {}
DOT_ENV_LOADED = load_dotenv()


def load_version() -> Dict[str, str]:
    """Stringify the __version__ module."""
    version_file_path = os.path.join(HERE, "__version__.py")
    spec = importlib.util.spec_from_file_location("__version__", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.__dict__


VERSION = load_version()


def get_semantic_version() -> str:
    """
    Return the semantic version number.

    Example valid values of __version__.py are:
    0.1.17
    0.1.17-next.1
    0.1.17-next.2
    0.1.17-next.123456
    0.1.17-next-major.1
    0.1.17-next-major.2
    0.1.17-next-major.123456

    Note:
    - pypi does not allow semantic version numbers to contain a dash.
    - pypi does not allow semantic version numbers to contain a 'v' prefix.
    - pypi does not allow semantic version numbers to contain a 'next' suffix.
    """
    version = VERSION["__version__"]
    version = re.sub(r"-next\.\d+", "", version)
    return re.sub(r"-next-major\.\d+", "", version)


class SettingsDefaults:
    """Default values for Settings"""

    AWS_PROFILE = TFVARS.get("aws_profile", None)
    AWS_ACCESS_KEY_ID = SecretStr(None)
    AWS_SECRET_ACCESS_KEY = SecretStr(None)
    AWS_REGION = TFVARS.get("aws_region", "us-east-1")

    DUMP_DEFAULTS = TFVARS.get("dump_defaults", False)
    DEBUG_MODE: bool = bool(TFVARS.get("debug_mode", False))
    SHARED_RESOURCE_IDENTIFIER = TFVARS.get("shared_resource_identifier", "rekognition_api")

    AWS_APIGATEWAY_CREATE_CUSTOM_DOMAIN = TFVARS.get("aws_apigateway_create_custom_domaim", False)
    AWS_APIGATEWAY_ROOT_DOMAIN = TFVARS.get("aws_apigateway_root_domain", None)

    AWS_DYNAMODB_TABLE_ID = "rekognition"

    AWS_REKOGNITION_COLLECTION_ID = AWS_DYNAMODB_TABLE_ID + "-collection"
    AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT: int = int(TFVARS.get("aws_rekognition_max_faces_count", 10))
    AWS_REKOGNITION_FACE_DETECT_THRESHOLD: int = int(TFVARS.get("aws_rekognition_face_detect_threshold", 10))
    AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES = TFVARS.get("aws_rekognition_face_detect_attributes", "DEFAULT")
    AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER = TFVARS.get("aws_rekognition_face_detect_quality_filter", "AUTO")

    @classmethod
    def to_dict(cls):
        """Convert SettingsDefaults to dict"""
        return {
            key: value
            for key, value in SettingsDefaults.__dict__.items()
            if not key.startswith("__") and not callable(key) and key != "to_dict"
        }


ec2 = boto3.Session().client("ec2")
regions = ec2.describe_regions()
AWS_REGIONS = [region["RegionName"] for region in regions["Regions"]]


def empty_str_to_bool_default(v: str, default: bool) -> bool:
    """Convert empty string to default boolean value"""
    if v in [None, ""]:
        return default
    return v.lower() in ["true", "1", "t", "y", "yes"]


def empty_str_to_int_default(v: str, default: int) -> int:
    """Convert empty string to default integer value"""
    if v in [None, ""]:
        return default
    try:
        return int(v)
    except ValueError:
        return default


# pylint: disable=too-many-public-methods
class Settings(BaseSettings):
    """Settings for Lambda functions"""

    _aws_session: boto3.Session = None
    _aws_access_key_id_source: str = "unset"
    _aws_secret_access_key_source: str = "unset"
    _dump: dict = None
    _initialized: bool = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        if bool(os.environ.get("AWS_DEPLOYED", False)):
            # If we're running inside AWS Lambda, then we don't need to set the AWS credentials.
            self._aws_access_key_id_source: str = "overridden by IAM role-based security"
            self._aws_secret_access_key_source: str = "overridden by IAM role-based security"
            self._aws_session = boto3.Session()
            self._initialized = True

        if not self._initialized and bool(os.environ.get("GITHUB_ACTIONS", False)):
            # Delete AWS_PROFILE from os.environ if it exists
            self._aws_session = boto3.Session(
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", None),
            )
            self._initialized = True

        if not self._initialized:
            if self.aws_profile:
                logger.debug("Using AWS_PROFILE: %s", self.aws_profile)
                self._aws_access_key_id_source = "aws_profile"
                self._aws_secret_access_key_source = "aws_profile"
                self._initialized = True

        if not self._initialized:
            if "aws_access_key_id" in data or "aws_secret_access_key" in data:
                if "aws_access_key_id" in data:
                    self._aws_access_key_id_source = "constructor"
                if "aws_secret_access_key" in data:
                    self._aws_secret_access_key_source = "constructor"
                self._initialized = True

        if not self._initialized:
            if "AWS_ACCESS_KEY_ID" in os.environ:
                self._aws_access_key_id_source = "environ"
            if "AWS_SECRET_ACCESS_KEY" in os.environ:
                self._aws_secret_access_key_source = "environ"

        if self.debug_mode:
            logger.setLevel(logging.DEBUG)

        # pylint: disable=logging-fstring-interpolation
        logger.debug(f"initialized settings: {self.aws_auth}")
        self._initialized = True

    shared_resource_identifier: Optional[str] = Field(
        SettingsDefaults.SHARED_RESOURCE_IDENTIFIER, env="SHARED_RESOURCE_IDENTIFIER"
    )
    debug_mode: Optional[bool] = Field(
        SettingsDefaults.DEBUG_MODE,
        env="DEBUG_MODE",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DEBUG_MODE),
    )
    dump_defaults: Optional[bool] = Field(
        SettingsDefaults.DUMP_DEFAULTS,
        env="DUMP_DEFAULTS",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.DUMP_DEFAULTS),
    )
    aws_profile: Optional[str] = Field(
        SettingsDefaults.AWS_PROFILE,
        env="AWS_PROFILE",
    )
    aws_access_key_id: Optional[SecretStr] = Field(
        SettingsDefaults.AWS_ACCESS_KEY_ID,
        env="AWS_ACCESS_KEY_ID",
    )
    aws_secret_access_key: Optional[SecretStr] = Field(
        SettingsDefaults.AWS_SECRET_ACCESS_KEY,
        env="AWS_SECRET_ACCESS_KEY",
    )
    aws_regions: Optional[List[str]] = Field(AWS_REGIONS, description="The list of AWS regions")
    aws_region: Optional[str] = Field(
        SettingsDefaults.AWS_REGION,
        env="AWS_REGION",
    )
    aws_apigateway_create_custom_domaim: Optional[bool] = Field(
        SettingsDefaults.AWS_APIGATEWAY_CREATE_CUSTOM_DOMAIN,
        env="AWS_APIGATEWAY_CREATE_CUSTOM_DOMAIN",
        pre=True,
        getter=lambda v: empty_str_to_bool_default(v, SettingsDefaults.AWS_APIGATEWAY_CREATE_CUSTOM_DOMAIN),
    )
    aws_apigateway_root_domain: Optional[str] = Field(
        SettingsDefaults.AWS_APIGATEWAY_ROOT_DOMAIN,
        env="AWS_APIGATEWAY_ROOT_DOMAIN",
    )
    aws_dynamodb_table_id: Optional[str] = Field(
        SettingsDefaults.AWS_DYNAMODB_TABLE_ID,
        env="AWS_DYNAMODB_TABLE_ID",
    )
    aws_rekognition_collection_id: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID,
        env="AWS_REKOGNITION_COLLECTION_ID",
    )

    aws_rekognition_face_detect_attributes: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES,
        env="AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES",
    )
    aws_rekognition_face_detect_quality_filter: Optional[str] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER,
        env="AWS_REKOGNITION_FACE_DETECT_QUALITY_FILTER",
    )
    aws_rekognition_face_detect_max_faces_count: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT),
    )
    aws_rekognition_face_detect_threshold: Optional[int] = Field(
        SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD,
        gt=0,
        env="AWS_REKOGNITION_FACE_DETECT_THRESHOLD",
        pre=True,
        getter=lambda v: empty_str_to_int_default(v, SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD),
    )

    @property
    def aws_account_id(self):
        """AWS account id"""
        return self.aws_session.client("sts").get_caller_identity()["Account"]

    @property
    def aws_access_key_id_source(self):
        """Source of aws_access_key_id"""
        return self._aws_access_key_id_source

    @property
    def aws_secret_access_key_source(self):
        """Source of aws_secret_access_key"""
        return self._aws_secret_access_key_source

    @property
    def aws_auth(self) -> dict:
        """AWS authentication"""
        return {
            "aws_profile": self.aws_profile,
            "aws_access_key_id_source": self.aws_access_key_id_source,
            "aws_secret_access_key_source": self.aws_secret_access_key_source,
            "aws_region": self.aws_region,
        }

    @property
    def aws_session(self):
        """AWS session"""
        if not self._aws_session:
            if self.aws_profile:
                logger.debug("creating new aws_session with aws_profile: %s", self.aws_profile)
                self._aws_session = boto3.Session(profile_name=self.aws_profile, region_name=self.aws_region)
                return self._aws_session
            if self.aws_access_key_id.get_secret_value() is not None and self.aws_secret_access_key is not None:
                logger.debug("creating new aws_session with aws keypair: %s", self.aws_access_key_id_source)
                self._aws_session = boto3.Session(
                    region_name=self.aws_region,
                    aws_access_key_id=self.aws_access_key_id.get_secret_value(),
                    aws_secret_access_key=self.aws_secret_access_key.get_secret_value(),
                )
                return self._aws_session
            logger.debug("creating new aws_session without aws credentials")
            self._aws_session = boto3.Session(region_name=self.aws_region)
        return self._aws_session

    @property
    def aws_apigateway_client(self):
        """API Gateway client"""
        return self.aws_session.client("apigateway")

    @property
    def aws_s3_client(self):
        """S3 client"""
        return self.aws_session.client("s3")

    @property
    def aws_dynamodb_client(self):
        """DynamoDB client"""
        return self.aws_session.client("dynamodb")

    @property
    def aws_rekognition_client(self):
        """Rekognition client"""
        return self.aws_session.client("rekognition")

    @property
    def dynamodb_table(self):
        """DynamoDB table"""
        return self.aws_dynamodb_client.Table(self.aws_dynamodb_table_id)

    @property
    def aws_s3_bucket_name(self) -> str:
        """Return the S3 bucket name."""
        return self.aws_account_id + "-" + self.shared_resource_identifier

    @property
    def aws_apigateway_name(self) -> str:
        """Return the API name."""
        return self.shared_resource_identifier + "-api"

    @property
    def aws_apigateway_domain_name(self) -> str:
        """Return the API domain."""
        if self.aws_apigateway_create_custom_domaim:
            return "api." + self.shared_resource_identifier + "." + self.aws_apigateway_root_domain

        try:
            response = self.aws_apigateway_client.get_rest_apis()
        except NoCredentialsError:
            # pylint: disable=logging-fstring-interpolation
            logger.error(f"NoCredentialsError. aws_auth: {self.aws_auth}")
            return None

        for item in response["items"]:
            if item["name"] == self.aws_apigateway_name:
                api_id = item["id"]
                return f"{api_id}.execute-api.{settings.aws_region}.amazonaws.com"
        return None

    @property
    def is_using_dotenv_file(self) -> bool:
        """Is the dotenv file being used?"""
        return DOT_ENV_LOADED

    @property
    def environment_variables(self) -> List[str]:
        """Environment variables"""
        return list(os.environ.keys())

    @property
    def is_using_tfvars_file(self) -> bool:
        """Is the tfvars file being used?"""
        return IS_USING_TFVARS

    @property
    def tfvars_variables(self) -> List[str]:
        """Terraform variables"""
        return list(TFVARS.keys())

    @property
    def is_using_aws_rekognition(self) -> bool:
        """Future: Is the AWS Rekognition service being used?"""
        return True

    @property
    def is_using_aws_dynamodb(self) -> bool:
        """Future: Is the AWS DynamoDB service being used?"""
        return True

    @property
    def version(self) -> str:
        """OpenAI API version"""
        return get_semantic_version()

    @property
    def dump(self) -> dict:
        """Dump all settings."""

        def recursive_sort_dict(d):
            return {k: recursive_sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(d.items())}

        def get_installed_packages():
            installed_packages = pkg_resources.working_set
            # pylint: disable=not-an-iterable
            package_list = [(d.project_name, d.version) for d in installed_packages]
            return package_list

        if self._dump and self._initialized:
            return self._dump

        packages = get_installed_packages()
        packages_dict = [{"name": name, "version": version} for name, version in packages]
        packages_json = json.dumps(packages_dict, indent=4)

        self._dump = {
            "environment": {
                "is_using_tfvars_file": self.is_using_tfvars_file,
                "is_using_dotenv_file": self.is_using_dotenv_file,
                "is_using_aws_rekognition": self.is_using_aws_rekognition,
                "is_using_aws_dynamodb": self.is_using_aws_dynamodb,
                "os": os.name,
                "system": platform.system(),
                "release": platform.release(),
                "boto3": boto3.__version__,
                "shared_resource_identifier": self.shared_resource_identifier,
                "debug_mode": self.debug_mode,
                "dump_defaults": self.dump_defaults,
                "version": self.version,
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "python_compiler": platform.python_compiler(),
                "python_build": platform.python_build(),
                "python_branch": platform.python_branch(),
                "python_revision": platform.python_revision(),
                "python_version_tuple": platform.python_version_tuple(),
                "python_installed_packages": packages_json,
            },
            "aws_auth": self.aws_auth,
            "aws_rekognition": {
                "aws_rekognition_collection_id": self.aws_rekognition_collection_id,
                "aws_rekognition_face_detect_max_faces_count": self.aws_rekognition_face_detect_max_faces_count,
                "aws_rekognition_face_detect_attributes": self.aws_rekognition_face_detect_attributes,
                "aws_rekognition_face_detect_quality_filter": self.aws_rekognition_face_detect_quality_filter,
                "aws_rekognition_face_detect_threshold": self.aws_rekognition_face_detect_threshold,
            },
            "aws_dynamodb": {
                "aws_dynamodb_table_id": self.aws_dynamodb_table_id,
            },
            "aws_apigateway": {
                "aws_apigateway_create_custom_domaim": self.aws_apigateway_create_custom_domaim,
                "aws_apigateway_name": self.aws_apigateway_name,
                "aws_apigateway_root_domain": self.aws_apigateway_root_domain,
                "aws_apigateway_domain_name": self.aws_apigateway_domain_name,
            },
            "aws_lambda": {},
            "aws_s3": {
                "aws_s3_bucket_prefix": self.aws_s3_bucket_name,
            },
            "terraform": {
                "tfvars": self.tfvars_variables,
            },
        }
        if self.dump_defaults:
            settings_defaults = SettingsDefaults.to_dict()
            self._dump["settings_defaults"] = settings_defaults

        if self.is_using_dotenv_file:
            self._dump["environment"]["dotenv"] = self.environment_variables

        if self.is_using_tfvars_file:
            self._dump["environment"]["tfvars"] = self.tfvars_variables

        self._dump = recursive_sort_dict(self._dump)
        return self._dump

    class Config:
        """Pydantic configuration"""

        frozen = True

    @field_validator("shared_resource_identifier")
    def validate_shared_resource_identifier(cls, v) -> str:
        """Validate shared_resource_identifier"""
        if v in [None, ""]:
            return SettingsDefaults.SHARED_RESOURCE_IDENTIFIER
        return v

    @field_validator("aws_profile")
    def validate_aws_profile(cls, v) -> str:
        """Validate aws_profile"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_PROFILE
        return v

    @field_validator("aws_access_key_id")
    def validate_aws_access_key_id(cls, v, values: ValidationInfo) -> str:
        """Validate aws_access_key_id"""
        if not isinstance(v, SecretStr):
            v = SecretStr(v)
        if v.get_secret_value() in [None, ""]:
            return SettingsDefaults.AWS_ACCESS_KEY_ID
        aws_profile = values.data.get("aws_profile", None)
        if aws_profile and len(aws_profile) > 0 and aws_profile != SettingsDefaults.AWS_PROFILE:
            # pylint: disable=logging-fstring-interpolation
            logger.warning(f"aws_access_key_id is being ignored. using aws_profile {aws_profile}.")
            return SettingsDefaults.AWS_ACCESS_KEY_ID
        return v

    @field_validator("aws_secret_access_key")
    def validate_aws_secret_access_key(cls, v, values: ValidationInfo) -> str:
        """Validate aws_secret_access_key"""
        if not isinstance(v, SecretStr):
            v = SecretStr(v)
        if v.get_secret_value() in [None, ""]:
            return SettingsDefaults.AWS_SECRET_ACCESS_KEY
        aws_profile = values.data.get("aws_profile", None)
        if aws_profile and len(aws_profile) > 0 and aws_profile != SettingsDefaults.AWS_PROFILE:
            # pylint: disable=logging-fstring-interpolation
            logger.warning(f"aws_secret_access_key is being ignored. using aws_profile {aws_profile}.")
            return SettingsDefaults.AWS_SECRET_ACCESS_KEY
        return v

    @field_validator("aws_region")
    # pylint: disable=no-self-argument,unused-argument
    def validate_aws_region(cls, v, values: ValidationInfo, **kwargs) -> str:
        """Validate aws_region"""
        valid_regions = values.data.get("aws_regions", [])
        if v in [None, ""]:
            return SettingsDefaults.AWS_REGION
        if v not in valid_regions:
            raise RekognitionValueError(f"aws_region {v} not in aws_regions")
        return v

    @field_validator("aws_apigateway_root_domain")
    def validate_aws_apigateway_root_domain(cls, v) -> str:
        """Validate aws_apigateway_root_domain"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_APIGATEWAY_ROOT_DOMAIN
        return v

    @field_validator("aws_apigateway_create_custom_domaim")
    def validate_aws_apigateway_create_custom_domaim(cls, v) -> bool:
        """Validate aws_apigateway_create_custom_domaim"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_APIGATEWAY_CREATE_CUSTOM_DOMAIN
        return v

    @field_validator("aws_dynamodb_table_id")
    def validate_table_id(cls, v) -> str:
        """Validate aws_dynamodb_table_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_DYNAMODB_TABLE_ID
        return v

    @field_validator("aws_rekognition_collection_id")
    def validate_collection_id(cls, v) -> str:
        """Validate aws_rekognition_collection_id"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_COLLECTION_ID
        return v

    @field_validator("aws_rekognition_face_detect_attributes")
    def validate_face_detect_attributes(cls, v) -> str:
        """Validate aws_rekognition_face_detect_attributes"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_ATTRIBUTES
        return v

    @field_validator("debug_mode")
    def parse_debug_mode(cls, v) -> bool:
        """Parse debug_mode"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DEBUG_MODE
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("dump_defaults")
    def parse_dump_defaults(cls, v) -> bool:
        """Parse dump_defaults"""
        if isinstance(v, bool):
            return v
        if v in [None, ""]:
            return SettingsDefaults.DUMP_DEFAULTS
        return v.lower() in ["true", "1", "t", "y", "yes"]

    @field_validator("aws_rekognition_face_detect_max_faces_count")
    def check_aws_rekognition_face_detect_max_faces_count(cls, v) -> int:
        """Check aws_rekognition_face_detect_max_faces_count"""
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_MAX_FACES_COUNT
        return int(v)

    @field_validator("aws_rekognition_face_detect_threshold")
    def check_face_detect_threshold(cls, v) -> int:
        """Check aws_rekognition_face_detect_threshold"""
        if isinstance(v, int):
            return v
        if v in [None, ""]:
            return SettingsDefaults.AWS_REKOGNITION_FACE_DETECT_THRESHOLD
        return int(v)


settings = None
try:
    settings = Settings()
except ValidationError as e:
    raise RekognitionConfigurationError("Invalid configuration: " + str(e)) from e
