## [0.2.14](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.13...v0.2.14) (2024-11-01)

### Bug Fixes

- force a new release ([447434a](https://github.com/FullStackWithLawrence/aws-rekognition/commit/447434a5b76786da538bfff28e5e4ebdadfd31bc))
- force a new release ([ef14fd2](https://github.com/FullStackWithLawrence/aws-rekognition/commit/ef14fd2c097c1d6dd79dd002b8ec2fb35a3feb30))

## [0.2.13](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.12...v0.2.13) (2024-08-01)

### Bug Fixes

- force a new release ([337ed44](https://github.com/FullStackWithLawrence/aws-rekognition/commit/337ed44efceb368a7a3721590243a46ba78edc90))
- force a new release ([24edc1c](https://github.com/FullStackWithLawrence/aws-rekognition/commit/24edc1c900f8af11566f7dce6f12405307877311))

## [0.2.12](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.11...v0.2.12) (2023-12-30)

### Bug Fixes

- add console logging when running inside of github actions. add init_info property ([56e3550](https://github.com/FullStackWithLawrence/aws-rekognition/commit/56e35503bf237817811a71191c5fabf5718705ab))
- echo IAM username ([fe59281](https://github.com/FullStackWithLawrence/aws-rekognition/commit/fe592816467c64f873ed95b6aebdbbb42df75573))

## [0.2.11](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.10...v0.2.11) (2023-12-23)

### Bug Fixes

- add Services class to control which services are enabled and should be tested ([c217965](https://github.com/FullStackWithLawrence/aws-rekognition/commit/c21796533a2b7a4c37bc61a0b42a0a82241d84d1))
- raise error if a disabled client setter is called ([8de3c2c](https://github.com/FullStackWithLawrence/aws-rekognition/commit/8de3c2c7cd70676c80314f8bab810eb55c24552e))

## [0.2.10](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.9...v0.2.10) (2023-12-22)

### Bug Fixes

- add policy attachments to roles. add a config to apigateway session w longer timeout ([ef2ffb7](https://github.com/FullStackWithLawrence/aws-rekognition/commit/ef2ffb7ee6ad76205d95ea5d1e2e7bba9ef3ab3d))

## [0.2.9](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.8...v0.2.9) (2023-12-22)

### Bug Fixes

- switch aws_s3_client to resource. lint lambda policy. ([d85bfae](https://github.com/FullStackWithLawrence/aws-rekognition/commit/d85bfae995076755d9b4e09e5c3cdfc952b50279))

## [0.2.8](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.7...v0.2.8) (2023-12-22)

### Bug Fixes

- add a copy of terraform.tfvars to rekognition_info lambda build ([4ca4b7a](https://github.com/FullStackWithLawrence/aws-rekognition/commit/4ca4b7a794b873eafb204feb66264bd712669c0b))
- add remaining aws infrastructure resource meta data to /info ([64630ea](https://github.com/FullStackWithLawrence/aws-rekognition/commit/64630ea05295112b67b9b6de3c744ba93422fe56))

## [0.2.7](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.6...v0.2.7) (2023-12-21)

### Bug Fixes

- add more permissions for lambda, for introspections ([56e29f1](https://github.com/FullStackWithLawrence/aws-rekognition/commit/56e29f18a81343f2f2941e5d695abaaedc657f30))
- post deployment tweaks ([169ea9e](https://github.com/FullStackWithLawrence/aws-rekognition/commit/169ea9e692358ab80cc0c8630a646719a3b026b9))

## [0.2.6](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.5...v0.2.6) (2023-12-21)

### Bug Fixes

- refactor aws infrastructure logic to AWSInfrastructureConfig() ([5f4f385](https://github.com/FullStackWithLawrence/aws-rekognition/commit/5f4f38576557d0b64e0c1407d124059a9a896bb7))

## [0.2.5](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.4...v0.2.5) (2023-12-20)

### Bug Fixes

- add a Terraform aws_deployed bool environment variable, to track whether we're running in prod ([d3aa46f](https://github.com/FullStackWithLawrence/aws-rekognition/commit/d3aa46fc3a78bf1181d58844ecc667f6a33fd351))

## [0.2.4](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.3...v0.2.4) (2023-12-20)

### Bug Fixes

- add aws key pair with validation and business rules, and unit tests ([e4d0710](https://github.com/FullStackWithLawrence/aws-rekognition/commit/e4d0710a88c3e04945e3227dc791cb0523e259ae))

## [0.2.3](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.2...v0.2.3) (2023-12-20)

### Bug Fixes

- raise throttle_settings_burst_limit=25 so that unit tests aren't throttled ([880be90](https://github.com/FullStackWithLawrence/aws-rekognition/commit/880be901e480a6f3ee79e649a1aa6f9af442d174))

## [0.2.2](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.1...v0.2.2) (2023-12-20)

### Bug Fixes

- integrate TFVARS to defaults. add conf meta fields. expand dump dict. ([c653aa1](https://github.com/FullStackWithLawrence/aws-rekognition/commit/c653aa10ab069272f6269d85fd1a04eb6ed0339b))

# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.2.1](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.2.0...v0.2.1) (2023-12-13)

### Bug Fixes

- hard code aws region ([0f10894](https://github.com/FullStackWithLawrence/aws-rekognition/commit/0f108941b59ee8047e23f345d3b52f3f542e781c))

# [0.2.0](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.1.2...v0.2.0) (2023-12-13)

### Features

- add Lambda Layer with Pydantic and dotenv ([612adb2](https://github.com/FullStackWithLawrence/aws-rekognition/commit/612adb2aed909f506560f00c2a4d34eb38bcbc4c))

## [0.2.0](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.1.2...v0.2.0) (2023-12-13)

### Features

- add Lambda Layer with Pydantic and dotenv ([612adb2](https://github.com/FullStackWithLawrence/aws-rekognition/commit/612adb2aed909f506560f00c2a4d34eb38bcbc4c))

## [0.1.2](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.1.1...v0.1.2) (2023-12-13)

### New Features

- add tests for .env file handling in conf.py ([b9eac51](https://github.com/FullStackWithLawrence/aws-rekognition/commit/b9eac5196683fc875941eca58a844d126b0ec51e))
- add unit test to configure Settings with constructor ([f818fe5](https://github.com/FullStackWithLawrence/aws-rekognition/commit/f818fe54d7f273faea3458014d6bf3c80556d468))
- add unit tests for read-only and negative attributes ([9c840a1](https://github.com/FullStackWithLawrence/aws-rekognition/commit/9c840a1a767081947cab1308cd29bfcfdaf46c02))
- add unit tests of pydantic range checking ([f9ec717](https://github.com/FullStackWithLawrence/aws-rekognition/commit/f9ec717af6b93b3fc1ddce51ed4b2dd9e8c33f4c))
- scaffold lambda test banks ([fe40ea2](https://github.com/FullStackWithLawrence/aws-rekognition/commit/fe40ea27ec59ff8cb137bbedc9d427222f2dbe11))

## [0.1.1](https://github.com/FullStackWithLawrence/aws-rekognition/compare/v0.1.0...v0.1.1) (2023-12-12)

### Bug Fixes

- force a new release ([1eb853b](https://github.com/FullStackWithLawrence/aws-rekognition/commit/1eb853b42b5c6c40abba05b39ac19e1af0ed16ff))

# 1.0.0 (2023-12-12)

### Bug Fixes

- force a new release ([385cf2d](https://github.com/FullStackWithLawrence/aws-rekognition/commit/385cf2d374de90197cb20acd8a8ce4a44816d61d))

## 0.0.0

**Commit Delta**: N/A

**Released**: 2023.09.03

**Summary**:

- Initial release!
