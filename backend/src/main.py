from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAPAOA_sWTznEtuTNUMBl64R2eU4AJwgUQ") # Use environment variable or fallback
GEMINI_API_URL = os.environ.get("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent")

@app.route("/generate_content", methods=["POST"])
def generate_content():
    data = request.json
    message = data.get("message")
    subject_id = data.get("subject_id")
    language = data.get("language")

    subject_context = {
        "mathematics": {
            "ar": "أنت مساعد ذكي متخصص في الرياضيات. ساعد الطلاب في حل المسائل الرياضية وشرح المفاهيم بطريقة مبسطة مع خطوات واضحة.",
            "en": "You are a smart assistant specialized in mathematics. Help students solve problems and explain concepts step by step in a simple way."
        },
        "physics": {
            "ar": "أنت مساعد ذكي متخصص في الفيزياء. قدّم شروحًا مبسطة مع القوانين الأساسية وخطوات الحل.",
            "en": "You are a smart assistant specialized in physics. Provide simplified explanations with key laws and step-by-step solutions."
        },
        "chemistry": {
            "ar": "أنت مساعد ذكي متخصص في الكيمياء. اشرح التفاعلات والقوانين مع أمثلة عملية.",
            "en": "You are a smart assistant specialized in chemistry. Explain reactions and rules with practical examples."
        },
        "arabic": {
            "ar": "أنت مساعد ذكي متخصص في اللغة العربية. اشرح القواعد والأدب مع أمثلة وتصحيح شائع للأخطاء.",
            "en": "You are a smart assistant specialized in Arabic. Explain grammar and literature with examples and common corrections."
        },
        "english": {
            "ar": "أنت مساعد ذكي متخصص في اللغة الإنجليزية. قدّم الشرح بالعربية والإنجليزية عند الحاجة.",
            "en": "You are a smart assistant specialized in English. Provide bilingual explanations when helpful."
        },
        "islamic": {
            "ar": "أنت مساعد ذكي متخصص في التربية الإسلامية. اشرح المفاهيم مع الاستدلال المناسب وبأسلوب مبسّط.",
            "en": "You are a smart assistant specialized in Islamic education. Explain concepts clearly with appropriate references."
        },
        "social_studies": {
            "ar": "أنت مساعد ذكي متخصص في الدراسات الاجتماعية. اشرح الأحداث التاريخية والجغرافيا والمجتمع بشكل موجز ومنظم.",
            "en": "You are a smart assistant specialized in social studies. Explain history, geography, and society clearly and concisely."
        }
    }

    system_prompt = subject_context.get(subject_id, {}).get(language, subject_context.get(subject_id, {}).get("ar", "أنت مساعد تعليمي ذكي."))
    
    # Fix for f-string syntax error
    lang_text = "العربية" if language == "ar" else "الإنجليزية"
    prompt = f"{system_prompt}\n\nسؤال الطالب: {message}\n\nيرجى تقديم إجابة مفصلة مع خطوات وأمثلة مختصرة باللغة {lang_text}."

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.6,
            "topP": 0.9,
            "topK": 40,
            "maxOutputTokens": 1024
        }
    }

    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        answer = ""
        if data.get("candidates") and len(data["candidates"]) > 0:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            answer = "\n\n".join([p.get("text") for p in parts if p.get("text")])

        if not answer:
            raise Exception("Invalid response format from Gemini API")

        return jsonify({"answer": answer})

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to connect to AI service. Please try again."}), 500
    except Exception as e:
        print(f"Error processing Gemini API response: {e}")
        return jsonify({"error": "Error processing AI response."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


