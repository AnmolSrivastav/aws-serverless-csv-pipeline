resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.file_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "s3.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.file_queue.arn
      Condition = {
        ArnEquals = { "aws:SourceArn" = aws_s3_bucket.sales_bucket.arn }
      }
    }]
  })
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.sales_bucket.id

  queue {
    queue_arn     = aws_sqs_queue.file_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".csv"
  }

  depends_on = [aws_sqs_queue_policy.allow_s3]
}
