from google import genai

client = genai.Client(api_key="AIzaSyDIM2KCwcE8I6EfyuabgLhiPEdfwWGRSDs")
response = client.models.generate_content(
    model = "gemini-2.0-flash", contents = input
)