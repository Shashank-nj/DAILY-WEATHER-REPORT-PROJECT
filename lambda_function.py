import json
import os
import urllib.request
import boto3


# --------------------------------------------------
# Configuration
# --------------------------------------------------

NTFY_TOPIC = os.environ["NTFY_TOPIC"]

BEDROCK_MODEL_ID = "meta.llama3-8b-instruct-v1:0"

AWS_REGION = "ap-south-1"


bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION
)


# --------------------------------------------------
# Weather code conversion
# --------------------------------------------------

def get_weather_description(code):

    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Rain showers",
        81: "Rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail"
    }

    return weather_codes.get(
        code,
        "Unknown weather"
    )


# --------------------------------------------------
# Get AI advice from Amazon Bedrock
# --------------------------------------------------

def get_ai_advice(
    temperature,
    humidity,
    condition,
    wind_speed
):

    prompt = f"""
You are a simple weather assistant.

Current Bengaluru weather:

Temperature: {temperature} °C
Humidity: {humidity}%
Condition: {condition}
Wind speed: {wind_speed} km/h

Give practical morning advice in exactly 2 short sentences.
Mention clothing and whether the person should consider carrying an umbrella.
Do not mention that you are an AI.
"""

    request_body = {
        "prompt": prompt,
        "max_gen_len": 100,
        "temperature": 0.5,
        "top_p": 0.9
    }

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(
        response["body"].read()
    )

    return response_body["generation"].strip()


# --------------------------------------------------
# Send notification using ntfy
# --------------------------------------------------

def send_notification(message):

    url = f"https://ntfy.sh/{NTFY_TOPIC}"

    request = urllib.request.Request(
        url,
        data=message.encode("utf-8"),
        method="POST"
    )

    request.add_header(
        "Title",
        "Bengaluru Weather + AI Advice"
    )

    request.add_header(
        "Priority",
        "default"
    )

    request.add_header(
        "Tags",
        "partly_sunny"
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:

        print("Notification sent successfully!")

        print(
            "ntfy response:",
            response.status
        )


# --------------------------------------------------
# Lambda handler
# --------------------------------------------------

def lambda_handler(event, context):

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=12.9716"
        "&longitude=77.5946"
        "&current=temperature_2m,"
        "relative_humidity_2m,"
        "weather_code,"
        "wind_speed_10m"
        "&timezone=Asia%2FKolkata"
    )

    try:

        # ------------------------------------------
        # 1. Get weather
        # ------------------------------------------

        with urllib.request.urlopen(
            weather_url,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        current = data["current"]

        temperature = current[
            "temperature_2m"
        ]

        humidity = current[
            "relative_humidity_2m"
        ]

        weather_code = current[
            "weather_code"
        ]

        wind_speed = current[
            "wind_speed_10m"
        ]

        condition = get_weather_description(
            weather_code
        )

        # ------------------------------------------
        # 2. Generate AI advice
        # ------------------------------------------

        ai_advice = get_ai_advice(
            temperature,
            humidity,
            condition,
            wind_speed
        )

        # ------------------------------------------
        # 3. Create notification
        # ------------------------------------------

        message = (
            "🌤️ Bengaluru Weather Update\n\n"

            f"🌡️ Temperature: "
            f"{temperature} °C\n"

            f"💧 Humidity: "
            f"{humidity}%\n"

            f"☁️ Condition: "
            f"{condition}\n"

            f"💨 Wind: "
            f"{wind_speed} km/h\n\n"

            "🤖 AI Advice:\n"

            f"{ai_advice}"
        )

        print(message)

        # ------------------------------------------
        # 4. Send notification
        # ------------------------------------------

        send_notification(message)

        return {
            "statusCode": 200,
            "body": json.dumps(message)
        }

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }