{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "rekognition:DescribeCollection",
        "rekognition:IndexFaces",
        "dynamodb:PutItem",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["${s3_bucket_arn}/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": [
        "${dynamodb_table_arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:IndexFaces",
        "rekognition:DescribeCollection"
        ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["ec2:DescribeRegions"],
      "Resource": "*"
    }
  ]
}