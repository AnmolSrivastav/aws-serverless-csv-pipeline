resource "aws_dynamodb_table" "results" {
  name         = "file-processing-results"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "file_name"

  attribute {
    name = "file_name"
    type = "S"
  }
}
