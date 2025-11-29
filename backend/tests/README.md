# Unit Tests - Backend

## Descripción

Este directorio contiene las pruebas unitarias del backend del proyecto Social Media Generator.

## Tests Implementados

### 1. ContentGenerator Tests (`test_content_generator.py`)
- **Test 1**: `test_is_academic_scope_valid` - Verifica detección de contenido académico válido
- **Test 2**: `test_is_academic_scope_invalid` - Verifica rechazo de contenido no académico
- **Test 3**: `test_is_academic_scope_empty` - Verifica manejo de texto vacío
- **Test 4**: `test_generate_social_content_success` - Verifica generación exitosa de contenido
- **Test 5**: `test_generate_social_content_out_of_scope` - Verifica rechazo de contenido fuera de alcance

### 2. MediaGenerator Tests (`test_media_generator.py`)
- **Test 6**: `test_generate_image_success` - Verifica generación exitosa de imágenes
- **Test 7**: `test_get_public_url_image` - Verifica generación de URLs públicas para imágenes
- **Test 8**: `test_get_public_url_video` - Verifica generación de URLs públicas para videos
- **Test 9**: `test_get_localhost_url` - Verifica generación de URLs localhost
- **Test 10**: `test_generate_image_no_client` - Verifica manejo de error sin cliente OpenAI

### 3. SocialPublisher Tests (`test_social_publisher.py`)
- **Test 11**: `test_publish_facebook_success` - Verifica publicación exitosa en Facebook
- **Test 12**: `test_publish_instagram_success` - Verifica publicación exitosa en Instagram
- **Test 13**: `test_publish_linkedin_success` - Verifica publicación exitosa en LinkedIn
- **Test 14**: `test_publish_tiktok_with_video` - Verifica publicación de video en TikTok
- **Test 15**: `test_publish_whatsapp_success` - Verifica publicación de historia en WhatsApp

## Instalación

```bash
# Instalar dependencias de testing
pip install pytest pytest-mock
```

## Ejecución de Tests

### Ejecutar todos los tests
```bash
cd backend
pytest
```

### Ejecutar tests con verbose
```bash
pytest -v
```

### Ejecutar un archivo específico
```bash
pytest tests/test_content_generator.py
```

### Ejecutar un test específico
```bash
pytest tests/test_content_generator.py::TestContentGenerator::test_is_academic_scope_valid
```

### Ver cobertura
```bash
pytest --cov=app --cov-report=html
```

## Estructura de Tests

Cada test sigue el patrón AAA:
- **Arrange**: Configuración inicial (setup_method)
- **Act**: Ejecución de la funcionalidad a probar
- **Assert**: Verificación de resultados esperados

## Mocking

Los tests utilizan `unittest.mock` para simular:
- Llamadas a APIs externas (OpenAI, Facebook, Instagram, etc.)
- Operaciones de I/O (archivos, requests HTTP)
- Variables de entorno

## Cobertura

Los tests cubren:
- ✅ Generación de contenido con OpenAI
- ✅ Validación de scope académico
- ✅ Generación de imágenes con DALL-E
- ✅ Gestión de URLs públicas y locales
- ✅ Publicación en 5 plataformas sociales
- ✅ Manejo de errores y excepciones

## Notas

- Los tests son **unitarios** y no requieren conexión a APIs reales
- Todos los servicios externos están mockeados
- No se necesita base de datos para ejecutar los tests
- Los tests son independientes entre sí
