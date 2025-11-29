import os
import json
from typing import List, Dict, Optional
from openai import OpenAI

class ContentGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def _is_academic_scope(self, text: str) -> bool:
        """Simple heuristic to determine if text is about academic/university topics."""
        if not text:
            return False
        txt = text.lower()
        academic_keywords = [
            "universidad", "campus", "investig", "tesis", "curso", "clase",
            "docente", "profesor", "estudiante", "académ", "investigación",
            "seminario", "congreso", "publicación", "artículo", "facultad",
            "departamento", "aniversario", "celebración", "retiro", "admisión",
            "inscripción", "matrícula", "convocatoria", "examen", "grado","ficct"
        ]
        for k in academic_keywords:
            if k in txt:
                return True
        return False

    def generate_social_content(self, title: str, body: str, platforms: List[str]) -> Dict[str, Dict]:
        """
        Generates social media content for the specified platforms.
        """
        combined_text = f"{title}\n\n{body}"
        
        # Enforce academic scope
        if not self._is_academic_scope(combined_text):
             return {t: {"error": "OUT_OF_SCOPE", "message": "Este asistente solo genera contenido académico/universitario."} for t in platforms}

        if not self.client:
            # Fallback if no API key (though plan assumes it exists, good for safety)
            return {t: {"error": "CONFIG_ERROR", "message": "OpenAI API Key not configured."} for t in platforms}

        system_prompt = (
            "Eres un experto community manager para una universidad prestigiosa. "
            "Tu tarea es generar contenido atractivo y específico para cada plataforma basado en el texto de entrada. "
            "Todo el contenido generado debe estar estrictamente en ESPAÑOL. "
            "Debes rechazar generar contenido para temas claramente fuera del ámbito académico o universitario. "
            "Devuelve un objeto JSON donde las claves son los nombres de las plataformas (en minúsculas) y los valores son objetos que contienen: "
            "- 'text': El texto/leyenda de la publicación (en español). "
            "- 'image_prompt': Un prompt "
            "detallado para generar una imagen para esta publicación (DALL-E). "
            "- 'hashtags': Una lista de hashtags relevantes (para Instagram/TikTok/LinkedIn). "
            "- 'script': (Solo para TikTok) Un guion corto para un video de 15-30s (en español). "
            "- 'tone': El tono utilizado (ej: Profesional, Casual, Emocionante). "
            "Responde SOLO con JSON válido."
        )

        user_prompt = (
            f"Title: {title}\nBody: {body}\n\n"
            f"Target Platforms: {', '.join(platforms)}\n\n"
            "Generate the content now."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
            )
            
            content_str = response.choices[0].message.content
            # Attempt to clean markdown code blocks if present
            if "```json" in content_str:
                content_str = content_str.split("```json")[1].split("```")[0].strip()
            elif "```" in content_str:
                content_str = content_str.split("```")[1].split("```")[0].strip()
                
            return json.loads(content_str)

        except Exception as e:
            print(f"Error generating content: {e}")
            return {t: {"error": "GENERATION_FAILED", "message": str(e)} for t in platforms}
