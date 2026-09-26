# 🌤️ AWS Daily Weather Notification Bot

A serverless AWS project that automatically collects weather information,
uses Amazon Bedrock to generate a short AI-based recommendation, and sends
the result as a notification using ntfy.

---

## 🚀 Project Architecture

```text
                 EventBridge Scheduler
                         |
                         | Scheduled trigger
                         v
                    AWS Lambda
                         |
              +----------+----------+
              |                     |
              v                     v
        Open-Meteo API        Amazon Bedrock
          Weather Data          Llama 3 8B
              |                     |
              +----------+----------+
                         |
                         v
                  Final Message
                         |
                         v
                      ntfy.sh
                         |
                         v
                    📱 Phone
