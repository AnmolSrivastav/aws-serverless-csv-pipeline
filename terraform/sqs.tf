resource "aws_sqs_queue" "dlq" {
  name = "file-processing-dlq"
}

resource "aws_sqs_queue" "file_queue" {
  name                       = "file-processing-queue"
  visibility_timeout_seconds = 60

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}
