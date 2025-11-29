import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.content_generator import ContentGenerator


class TestContentGenerator:
    
    def setup_method(self):
        self.generator = ContentGenerator()
    
    def test_is_academic_scope_valid(self):
        text = "La universidad convoca a nuevos estudiantes para el semestre 2025"
        result = self.generator._is_academic_scope(text)
        assert result is True, "Debe detectar contenido académico"
    
    def test_is_academic_scope_invalid(self):
        text = "Oferta de pizzas en el restaurante de la esquina"
        result = self.generator._is_academic_scope(text)
        assert result is False, "Debe rechazar contenido no académico"
    
    def test_is_academic_scope_empty(self):
        result = self.generator._is_academic_scope("")
        assert result is False, "El texto vacío no debe ser académico"
    
    @patch('app.services.content_generator.OpenAI')
    def test_generate_social_content_success(self, mock_openai):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''{
            "facebook": {
                "text": "Contenido para Facebook",
                "image_prompt": "Universidad campus",
                "hashtags": ["#Universidad"],
                "tone": "Profesional"
            }
        }'''
        mock_client.chat.completions.create.return_value = mock_response
        
        generator = ContentGenerator()
        generator.client = mock_client
        
        result = generator.generate_social_content(
            "Nuevo curso", 
            "La universidad abre inscripciones", 
            ["facebook"]
        )
        
        assert "facebook" in result
        assert result["facebook"]["text"] == "Contenido para Facebook"
        assert "error" not in result["facebook"]
    
    @patch('app.services.content_generator.OpenAI')
    def test_generate_social_content_out_of_scope(self, mock_openai):
        generator = ContentGenerator()
        generator.client = MagicMock()
        
        result = generator.generate_social_content(
            "Pizza Sale",
            "Buy pizzas today with 50% discount",
            ["facebook"]
        )
        
        assert "facebook" in result
        assert result["facebook"]["error"] == "OUT_OF_SCOPE"
        assert "académico" in result["facebook"]["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
