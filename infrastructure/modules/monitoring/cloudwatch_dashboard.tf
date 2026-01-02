###############################################################################
# CloudWatch Dashboard for Seoul Economic Daily
#
# 대기업급 모니터링 대시보드:
# - CloudFront (CDN) 성능
# - API Gateway (백엔드 API) 응답시간
# - EC2 (웹서버) 리소스 사용률
# - Lambda (서버리스) 실행 통계
###############################################################################

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-infrastructure-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      # ========================================================================
      # Row 1: CloudFront Metrics (CDN 성능)
      # ========================================================================
      {
        type = "metric"
        x    = 0
        y    = 0
        width = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/CloudFront", "Requests", { stat = "Sum", label = "총 요청 수" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "📊 CloudFront - 총 요청 수 (Requests)"
          period  = 300
          yAxis = {
            left = {
              label = "Requests"
            }
          }
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 0
        width = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/CloudFront", "BytesDownloaded", { stat = "Sum", label = "다운로드 데이터" }],
            [".", "BytesUploaded", { stat = "Sum", label = "업로드 데이터" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "📡 CloudFront - 데이터 전송량 (Bytes)"
          period  = 300
          yAxis = {
            left = {
              label = "Bytes"
            }
          }
        }
      },

      # ========================================================================
      # Row 2: CloudFront Error Rates (에러율)
      # ========================================================================
      {
        type = "metric"
        x    = 0
        y    = 6
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/CloudFront", "4xxErrorRate", { stat = "Average", label = "4xx 에러율", color = "#ff7f0e" }],
            [".", "5xxErrorRate", { stat = "Average", label = "5xx 에러율", color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "⚠️ CloudFront - 에러율 (%)"
          period  = 300
          yAxis = {
            left = {
              label = "Error Rate (%)"
              min   = 0
            }
          }
        }
      },
      {
        type = "metric"
        x    = 8
        y    = 6
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/CloudFront", "CacheHitRate", { stat = "Average", label = "캐시 적중률" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "💾 CloudFront - 캐시 적중률 (%)"
          period  = 300
          yAxis = {
            left = {
              label = "Cache Hit Rate (%)"
              min   = 0
              max   = 100
            }
          }
        }
      },
      {
        type = "metric"
        x    = 16
        y    = 6
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/CloudFront", "OriginLatency", { stat = "Average", label = "Origin 지연시간" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "⏱️ CloudFront - Origin 응답시간 (ms)"
          period  = 300
          yAxis = {
            left = {
              label = "Latency (ms)"
            }
          }
        }
      },

      # ========================================================================
      # Row 3: API Gateway Metrics (백엔드 API 성능)
      # ========================================================================
      {
        type = "metric"
        x    = 0
        y    = 12
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", { stat = "Sum", label = "API 호출 수" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "🔌 API Gateway - 총 호출 수"
          period  = 300
        }
      },
      {
        type = "metric"
        x    = 8
        y    = 12
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/ApiGateway", "Latency", { stat = "Average", label = "평균 지연시간", color = "#1f77b4" }],
            [".", "IntegrationLatency", { stat = "Average", label = "Lambda 실행시간", color = "#ff7f0e" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "⏱️ API Gateway - 응답 시간 (ms)"
          period  = 300
          yAxis = {
            left = {
              label = "Latency (ms)"
            }
          }
        }
      },
      {
        type = "metric"
        x    = 16
        y    = 12
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/ApiGateway", "4XXError", { stat = "Sum", label = "4xx 에러", color = "#ff7f0e" }],
            [".", "5XXError", { stat = "Sum", label = "5xx 에러", color = "#d62728" }]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.region
          title   = "❌ API Gateway - 에러 수"
          period  = 300
        }
      },

      # ========================================================================
      # Row 4: EC2 Instance Metrics (웹서버 리소스)
      # ========================================================================
      {
        type = "metric"
        x    = 0
        y    = 18
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", { stat = "Average", label = "CPU 사용률" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "🖥️ EC2 - CPU 사용률 (%)"
          period  = 300
          yAxis = {
            left = {
              label = "CPU (%)"
              min   = 0
              max   = 100
            }
          }
          annotations = {
            horizontal = [
              {
                label = "경고 임계값"
                value = 80
                fill  = "above"
                color = "#ff7f0e"
              },
              {
                label = "위험 임계값"
                value = 90
                fill  = "above"
                color = "#d62728"
              }
            ]
          }
        }
      },
      {
        type = "metric"
        x    = 8
        y    = 18
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/EC2", "NetworkIn", { stat = "Sum", label = "Network In" }],
            [".", "NetworkOut", { stat = "Sum", label = "Network Out" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "🌐 EC2 - 네트워크 트래픽 (Bytes)"
          period  = 300
          yAxis = {
            left = {
              label = "Bytes"
            }
          }
        }
      },
      {
        type = "metric"
        x    = 16
        y    = 18
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/EC2", "StatusCheckFailed", { stat = "Sum", label = "상태 체크 실패" }],
            [".", "StatusCheckFailed_Instance", { stat = "Sum", label = "인스턴스 체크 실패" }],
            [".", "StatusCheckFailed_System", { stat = "Sum", label = "시스템 체크 실패" }]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.region
          title   = "🔍 EC2 - 상태 체크"
          period  = 300
        }
      },

      # ========================================================================
      # Row 5: Lambda Function Metrics (서버리스 함수)
      # ========================================================================
      {
        type = "metric"
        x    = 0
        y    = 24
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum", label = "Lambda 실행 수" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "⚡ Lambda - 총 실행 수"
          period  = 300
        }
      },
      {
        type = "metric"
        x    = 8
        y    = 24
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", { stat = "Average", label = "평균 실행시간" }],
            [".", "Duration", { stat = "Maximum", label = "최대 실행시간" }]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "⏱️ Lambda - 실행 시간 (ms)"
          period  = 300
          yAxis = {
            left = {
              label = "Duration (ms)"
            }
          }
        }
      },
      {
        type = "metric"
        x    = 16
        y    = 24
        width = 8
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Errors", { stat = "Sum", label = "에러", color = "#d62728" }],
            [".", "Throttles", { stat = "Sum", label = "제한", color = "#ff7f0e" }]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.region
          title   = "❌ Lambda - 에러 & 제한"
          period  = 300
        }
      },

      # ========================================================================
      # Row 6: Cost Estimation (비용 추정)
      # ========================================================================
      {
        type = "metric"
        x    = 0
        y    = 30
        width = 24
        height = 6

        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", { stat = "Maximum", label = "예상 비용 (USD)" }]
          ]
          view    = "singleValue"
          region  = "us-east-1"
          title   = "💰 AWS 월별 예상 비용 (USD)"
          period  = 86400
        }
      }
    ]
  })
}

# Output the dashboard URL
output "cloudwatch_dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}
