from rest_framework.decorators import api_view # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect # type: ignore
from django.shortcuts import redirect # type: ignore
from urllib.parse import urlencode
import os
import json
import base64
import openai # type: ignore
from google.auth.transport.requests import Request, AuthorizedSession # type: ignore
from google_auth_oauthlib.flow import Flow # type: ignore
from google.oauth2.credentials import Credentials # type: ignore
from googleapiclient.discovery import build # type: ignore
from django.core.cache import cache  # type: ignore # 
from dotenv import load_dotenv  # type: ignore # 


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://mail.google.com/"
]
REDIRECT_URI = "http://127.0.0.1:8000/api/auth/callback/"

@api_view(['GET'])
def google_login(request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES, 
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')

    print(f"🔍 Redirecting to Google OAuth: {auth_url}")

    return HttpResponseRedirect(auth_url)

@api_view(["GET"])
def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Missing authorization code"}, status=400)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_info = get_google_user_info(credentials)
    if "error" in user_info:
        return JsonResponse(user_info, status=500)
    print(f"✅ Google User Info: {user_info}")  

    service = authenticate_gmail_with_user_token(credentials)

    emails = fetch_recent_emails(service)
    if not emails:
        return JsonResponse({"error": "No emails found"}, status=404)
    print(f"✅ Fetched Emails: {emails}") 

    analyzed_emails = []
    for email in emails:
        analysis = analyze_email_content(email["subject"], email["body"])
        analyzed_emails.append({
            "id": email["id"],
            "subject": email["subject"],
            "category": analysis.get("category", "unknown"),
            "spam_score": analysis.get("spam_score", "unknown"),
            "should_delete": analysis.get("should_delete", "unknown")
        })

    print(f"✅ Email Analysis Results: {analyzed_emails}")  

    cache.set(f"emails_{user_info['email']}", analyzed_emails, timeout=600)

    return JsonResponse({
        "message": "Login successful, emails analyzed.",
        "user": user_info,
        "emails": analyzed_emails
    }, status=200)

def fetch_recent_emails(service, max_results=5):
    try:
        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])

        print(f"🔍 Raw Gmail API Response: {results}")

        if not messages:
            print("⚠️ No emails found!")
            return []

        emails = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
            headers = msg_data["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            body, _ = extract_email_body(msg_data.get("payload", {}))

            emails.append({
                "id": msg["id"],
                "subject": subject,
                "body": body
            })

        return emails

    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []


def get_google_user_info(credentials):
    from google.auth.transport.requests import AuthorizedSession # type: ignore
    authed_session = AuthorizedSession(credentials)

    response = authed_session.get("https://www.googleapis.com/oauth2/v3/userinfo")

    print(f"🔍 Google API Response Code: {response.status_code}") 
    print(f"🔍 Google API Response Body: {response.text}")

    if response.status_code != 200 or not response.text.strip():
        print(f"❌ Google API Error: {response.status_code}, Response: {response.text}")
        return {"error": "Failed to fetch user info from Google"}

    return response.json()

def authenticate_gmail_with_user_token(credentials):
    if isinstance(credentials, dict):
        raise TypeError("Expected `Credentials` object, but got a dictionary.")

    return build("gmail", "v1", credentials=credentials)

def analyze_email_content(subject, body):
    messages = [
        {"role": "system", "content": "You are an AI that classifies emails into spam, promotions, or important."},
        {"role": "user", "content": f"Analyze this email:\n\nSubject: {subject}\nBody: {body}"},
        {"role": "user", "content": """ 
        1. Is this email spam, promotional, or important? Respond with "spam", "promotion", or "important".
        2. Provide a spam score (0-100%).
        3. Should this email be deleted? Respond with "yes" or "no".
        
        Return JSON:
        {
            "category": "spam/promotion/important",
            "spam_score": "integer (0-100%)",
            "should_delete": "yes" or "no"
        }
        """}
    ]

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2
        )

        print(f"🔍 OpenAI API Response: {response}") 

        if not response or not response.choices or not response.choices[0].message.content.strip():
            print("❌ OpenAI API returned an empty response!")
            return {"error": "No response from OpenAI"}

        return json.loads(response.choices[0].message.content)

    except openai.OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return {"error": "Failed to analyze email"}


def extract_email_body(payload):

    body = None
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                body = decode_email_body(part["body"].get("data", ""))
    else:
        body = decode_email_body(payload["body"].get("data", ""))

    return body, None

def decode_email_body(encoded_body):

    if not encoded_body:
        return None
    return base64.urlsafe_b64decode(encoded_body).decode("utf-8", errors="ignore")

def analyze_email_content(subject, body):

    messages = [
        {"role": "system", "content": "You are an AI that classifies emails into spam, promotions, or important."},
        {"role": "user", "content": f"Analyze this email:\n\nSubject: {subject}\nBody: {body}"},
        {"role": "user", "content": """ 
        1. Is this email spam, promotional, or important? Respond with "spam", "promotion", or "important".
        2. Provide a spam score (0-100%).
        3. Should this email be deleted? Respond with "yes" or "no".
        
        Return JSON:
        {
            "category": "spam/promotion/important",
            "spam_score": "integer (0-100%)",
            "should_delete": "yes" or "no"
        }
        """}
    ]

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2
        )

        print(f"🔍 OpenAI API Response: {response}")  

        if not response or not response.choices or not response.choices[0].message.content.strip():
            print("❌ OpenAI API returned an empty response!")
            return {"error": "No response from OpenAI"}

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"❌ OpenAI JSON Decode Error: {e}")
            return {"error": "Invalid JSON from OpenAI"}
    except openai.OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return {"error": "Failed to analyze email"}



@api_view(["GET"])
def get_analyzed_emails(request):
    user_email = request.GET.get("email")

    if not user_email:
        print("❌ Error: User email is missing in the request.")
        return JsonResponse({"error": "User email required"}, status=400)

    emails = cache.get(f"emails_{user_email}")

    if emails is None:
        print(f"⚠️ No analyzed emails found for {user_email}.")
        return JsonResponse({"message": "No analyzed emails found for this user."}, status=404)

    print(f"✅ Returning {len(emails)} analyzed emails for {user_email}.")
    
    return JsonResponse({"emails": emails}, status=200)

