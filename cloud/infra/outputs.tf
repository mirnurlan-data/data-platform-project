output "raw_bucket_name" {
  value       = aws_s3_bucket.raw.id
  description = "Bucket name for the synthetic source batches."
}

output "raw_prefix_policy_arn" {
  value       = aws_iam_policy.raw_sales_reader_writer.arn
  description = "Unattached least-privilege policy. Review before attaching to workload role."
}
