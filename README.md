# Social Topicos - Generador de Contenido para Redes Sociales

Sistema automatizado de generación y publicación de contenido para redes sociales, diseñado específicamente para universidades y instituciones educativas. Utiliza inteligencia artificial (OpenAI GPT y DALL-E) para crear contenido personalizado y publicarlo directamente en múltiples plataformas sociales.

## 🎯 Descripción del Proyecto

Social Topicos es una herramienta integral que automatiza el proceso completo de creación y publicación de contenido en redes sociales:

1. **Generación con IA**: Utiliza GPT para generar texto adaptado a cada plataforma y DALL-E para crear imágenes personalizadas
2. **Validación de Contexto**: Solo genera contenido relacionado con temas académicos y universitarios
3. **Publicación Directa**: Publica instantáneamente en Facebook, Instagram, LinkedIn, TikTok y WhatsApp
4. **Gestión de Usuarios**: Sistema de autenticación con historial de publicaciones por usuario
5. **Generación de Videos**: Crea automáticamente videos para TikTok a partir de imágenes

## 🚀 Quick Start

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/your-username/LLM_Social_Topicos.git
cd LLM_Social_Topicos

# 2. Configurar variables de entorno
cp .env.example backend/.env
# Editar backend/.env con tus API keys

# 3. Iniciar con Docker
chmod +x start.sh
./start.sh
```

Accede a la aplicación en: **http://localhost**

### Opción 2: Desarrollo Local

#### Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### Frontend (Angular)

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
ng serve
```

Accede a: **http://localhost:4200**

---

## 📦 Stack Tecnológico

### Backend
- **FastAPI** - Framework web asíncrono de alto rendimiento
- **PostgreSQL 15** - Base de datos relacional para usuarios y publicaciones
- **OpenAI GPT-3.5/4** - Generación inteligente de contenido
- **DALL-E 3** - Generación de imágenes personalizadas
- **SQLAlchemy** - ORM para gestión de base de datos
- **MoviePy** - Procesamiento y creación de videos para TikTok
- **JWT** - Autenticación segura con tokens

### Frontend
- **Angular 18** - Framework frontend moderno
- **TypeScript** - Lenguaje tipado para mejor desarrollo
- **RxJS** - Programación reactiva para manejo de estados

### APIs de Redes Sociales
- **Meta Graph API** - Facebook e Instagram
- **LinkedIn API v2** - Publicaciones profesionales
- **TikTok Content Posting API** - Videos cortos
- **Whapi.cloud** - WhatsApp Business Stories

### Infraestructura
- **Docker & Docker Compose** - Containerización y orquestación
- **Nginx** - Reverse proxy y servidor de archivos estáticos
- **PostgreSQL** - Almacenamiento persistente

---

## 🏗️ Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                      Cliente (Navegador)                      │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTP/HTTPS
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    Nginx (Puerto 80)                          │
│  - Reverse Proxy                                             │
│  - Servidor de archivos estáticos                           │
└────────────┬──────────────────────────────┬──────────────────┘
             │                              │
             │ /                            │ /api/*
             ▼                              ▼
┌─────────────────────┐         ┌───────────────────────────────┐
│  Angular Frontend   │         │   FastAPI Backend (Puerto 8080)│
│  (Puerto 4200)      │         │                                │
│  - UI Components    │         │  ┌──────────────────────────┐  │
│  - State Management │         │  │   API Endpoints          │  │
│  - HTTP Client      │         │  │  - /generate (POST)      │  │
└─────────────────────┘         │  │  - /publish (POST)       │  │
                                │  │  - /auth/* (POST/GET)    │  │
                                │  │  - /publications (GET)   │  │
                                │  └────────┬─────────────────┘  │
                                │           │                    │
                                │  ┌────────▼─────────────────┐  │
                                │  │  Services Layer          │  │
                                │  │  - ContentGenerator      │  │
                                │  │  - MediaGenerator        │  │
                                │  │  - SocialPublisher       │  │
                                │  └────────┬─────────────────┘  │
                                └───────────┼────────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
        ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
        │   PostgreSQL     │   │   OpenAI API     │   │  Social Media    │
        │   (Puerto 5433)  │   │                  │   │     APIs         │
        │                  │   │  - GPT-3.5/4     │   │                  │
        │  - users         │   │  - DALL-E 3      │   │  - Facebook      │
        │  - publications  │   │                  │   │  - Instagram     │
        │  - chat_sessions │   └──────────────────┘   │  - LinkedIn      │
        │  - chat_messages │                          │  - TikTok        │
        └──────────────────┘                          │  - WhatsApp      │
                                                      └──────────────────┘
```

### Flujo de Publicación

```
1. Usuario ingresa título y cuerpo → Frontend
                ↓
2. POST /api/generate → Backend
                ↓
3. ContentGenerator valida scope académico
                ↓
4. OpenAI GPT genera contenido por plataforma
                ↓
5. MediaGenerator crea imagen con DALL-E
                ↓
6. Si es TikTok: MoviePy crea video de 6s
                ↓
7. Usuario revisa y confirma → Frontend
                ↓
8. POST /api/publish → Backend
                ↓
9. SocialPublisher envía a cada plataforma
                ↓
10. Guarda registro en PostgreSQL (publications)
                ↓
11. Retorna resultados → Frontend
```

### Sistema de Publicación Directa

**Sin colas ni workers en segundo plano:**
- ✅ Publicación inmediata y síncrona
- ✅ Respuesta instantánea al usuario
- ✅ Feedback directo de éxito/error por plataforma
- ✅ Arquitectura simple y mantenible
- ✅ Sin dependencias de Redis o Celery
- ✅ Menor complejidad operacional

---

## 🎯 Características Principales

### ✨ Generación Inteligente de Contenido
- **GPT-3.5/4**: Genera posts personalizados y adaptados a cada red social
- **DALL-E 3**: Crea imágenes únicas basadas en el contenido
- **Contexto Académico**: Valida que el contenido sea relevante para universidades
- **Multi-Plataforma**: Adapta automáticamente el tono y formato para cada red

### 📱 Publicación en 5 Plataformas
- **Facebook**: Posts con imagen y texto en páginas institucionales
- **Instagram**: Posts visuales con caption y hashtags
- **LinkedIn**: Contenido profesional para networking académico
- **TikTok**: Videos cortos de 6 segundos con imagen y texto
- **WhatsApp**: Stories con imagen para difusión rápida

### 🎥 Generación Automática de Videos
- Crea videos de 6 segundos para TikTok usando MoviePy
- Convierte imágenes estáticas en contenido dinámico
- Optimización automática de formato (yuv420p, 30fps)

### 👥 Sistema de Autenticación y Usuarios
- Registro e inicio de sesión con JWT
- Historial de publicaciones por usuario
- Endpoints protegidos con autenticación
- Gestión de sesiones de chat

### 💬 Interfaz de Chat Interactiva
- Diseño tipo ChatGPT para generación de contenido
- Historial de conversaciones persistente
- Generación iterativa y refinamiento de posts
- Feedback en tiempo real

### 📊 Gestión de Publicaciones
- Registro completo de cada publicación
- Estado por plataforma (éxito/error)
- Mensajes de error detallados para debugging
- Consulta de historial por usuario

---

## 🐳 Despliegue en Producción

### AWS EC2

Consulta la guía completa en [DEPLOYMENT.md](DEPLOYMENT.md)

**Resumen rápido:**

```bash
# En tu servidor EC2 (Ubuntu 22.04)

# 1. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Clonar repositorio
git clone https://github.com/your-username/LLM_Social_Topicos.git
cd LLM_Social_Topicos

# 3. Configurar environment
cp .env.example backend/.env
nano backend/.env  # Agregar tus API keys

# 4. Desplegar
docker-compose up -d --build

# 5. Verificar
curl http://localhost/health
```

Accede a: **http://your-ec2-public-ip**

---

## 📋 Variables de Entorno

Crea `backend/.env` con:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/social_topicos

# JWT Authentication
SECRET_KEY=your-secret-key-here-change-in-production

# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Facebook/Instagram (Meta Graph API)
FB_PAGE_ACCESS_TOKEN=your-long-lived-page-access-token
FB_PAGE_ID=your-facebook-page-id
IG_BUSINESS_ACCOUNT_ID=your-instagram-business-account-id

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your-linkedin-oauth-token
LINKEDIN_AUTHOR_URN=urn:li:person:YOUR_ID

# TikTok Content Posting API
TIKTOK_ACCESS_TOKEN=act.your-tiktok-access-token

# WhatsApp Business (Whapi.cloud)
WHAPI_TOKEN=your-whapi-cloud-token
```

---

## 🔧 Comandos Útiles

### Docker

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir
docker-compose up -d --build

# Ver estado
docker-compose ps
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker exec -it social_topicos_db psql -U postgres -d social_topicos

# Backup
docker exec social_topicos_db pg_dump -U postgres social_topicos > backup.sql

# Restore
docker exec -i social_topicos_db psql -U postgres -d social_topicos < backup.sql
```

### Desarrollo

```bash
# Backend - Crear migración
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head

# Frontend - Build para producción
cd frontend
npm run build
```

---

## 📊 Endpoints API Principales

### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión (retorna JWT)
- `GET /api/auth/me` - Obtener usuario autenticado actual

### Generación de Contenido
- `POST /api/generate` - Generar contenido con IA para múltiples plataformas
  ```json
  {
    "title": "Título del post",
    "body": "Descripción del contenido",
    "platforms": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
  }
  ```

### Publicaciones
- `POST /api/publish` - Publicar contenido en redes sociales seleccionadas
- `GET /api/publications` - Listar todas las publicaciones
- `GET /api/publications/me` - Publicaciones del usuario actual
- `GET /api/publications/{id}` - Obtener detalle de una publicación

### Chat
- `GET /api/chats` - Listar sesiones de chat del usuario
- `GET /api/chats/{id}` - Obtener conversación específica
- `POST /api/chats/{id}/messages` - Agregar mensaje a chat

### Sistema
- `GET /health` - Health check del sistema

**Documentación interactiva completa:** `http://localhost:8080/docs` (Swagger UI)

---

## 🧪 Testing

El proyecto incluye 15 pruebas unitarias que cubren las funcionalidades principales:

```bash
# Ejecutar tests dentro del contenedor
docker-compose exec backend python -m pytest tests/ -v

# Ver cobertura
docker-compose exec backend python -m pytest tests/ --cov=app --cov-report=html

# Tests específicos
docker-compose exec backend python -m pytest tests/test_content_generator.py -v
```

**Cobertura de Tests:**
- ✅ Generación de contenido con validación de scope académico
- ✅ Generación de imágenes con DALL-E
- ✅ Gestión de URLs públicas y locales
- ✅ Publicación en 5 plataformas sociales
- ✅ Manejo de errores y excepciones

---

## 📝 Estructura del Proyecto

```
LLM_Social_Final/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py         # Autenticación JWT
│   │   │   │   └── chat.py         # Chat interactivo
│   │   │   ├── api.py              # Router principal
│   │   │   ├── deps.py             # Dependencias (get_current_user)
│   │   │   └── routes.py           # Endpoints de generación y publicación
│   │   ├── core/
│   │   │   ├── config.py           # Configuración y variables de entorno
│   │   │   └── security.py         # Hash de passwords y JWT
│   │   ├── db/
│   │   │   ├── base.py             # Base de SQLAlchemy
│   │   │   └── session.py          # Sesión de base de datos
│   │   ├── models/
│   │   │   ├── user.py             # Modelo de usuario
│   │   │   ├── publication.py      # Modelo de publicación
│   │   │   └── chat.py             # Modelos de chat
│   │   ├── services/
│   │   │   ├── content_generator.py    # Generación con GPT
│   │   │   ├── media_generator.py      # Imágenes con DALL-E
│   │   │   ├── social_publisher.py     # Orquestador de publicaciones
│   │   │   └── publishers/
│   │   │       ├── base.py             # Clase base
│   │   │       ├── facebook.py         # Facebook Graph API
│   │   │       ├── instagram.py        # Instagram Graph API
│   │   │       ├── linkedin.py         # LinkedIn API
│   │   │       ├── tiktok.py           # TikTok Content API
│   │   │       └── whatsapp.py         # WhatsApp via Whapi.cloud
│   │   └── main.py                     # Aplicación FastAPI principal
│   ├── static/
│   │   ├── media/                      # Imágenes generadas
│   │   └── videos/                     # Videos para TikTok
│   ├── tests/
│   │   ├── test_content_generator.py   # Tests de generación
│   │   ├── test_media_generator.py     # Tests de medios
│   │   └── test_social_publisher.py    # Tests de publicación
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── content-generator/  # Generador de contenido
│   │   │   │   ├── login/              # Login de usuarios
│   │   │   │   └── register/           # Registro de usuarios
│   │   │   ├── services/
│   │   │   │   └── api.service.ts      # Cliente HTTP para backend
│   │   │   ├── app.component.ts
│   │   │   └── app.routes.ts           # Rutas de Angular
│   │   └── index.html
│   ├── Dockerfile
│   ├── nginx.conf                      # Configuración de Nginx
│   └── package.json
├── docker-compose.yml                  # Orquestación de servicios
├── COMANDOS.md                         # Comandos útiles del proyecto
├── DEPLOYMENT.md                       # Guía de despliegue
└── README.md                           # Este archivo
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 🆘 Soporte y Documentación

- **Comandos Útiles**: [COMANDOS.md](COMANDOS.md) - Guía de comandos Docker, DB y testing
- **Despliegue**: [DEPLOYMENT.md](DEPLOYMENT.md) - Instrucciones para producción
- **Dependencias**: [DEPENDENCIES.md](DEPENDENCIES.md) - Análisis de dependencias del proyecto
- **API Docs**: http://localhost:8080/docs - Documentación interactiva Swagger
- **Issues**: [GitHub Issues](https://github.com/jcarlosdelgado/Social-Topicos/issues)

---

## 🎓 Acerca del Proyecto

**Social Topicos** es una solución completa para la gestión automatizada de contenido en redes sociales, específicamente diseñada para instituciones educativas y universidades. 

### Objetivo
Facilitar la creación y publicación de contenido relevante, atractivo y profesional en múltiples plataformas sociales mediante el uso de inteligencia artificial, reduciendo el tiempo y esfuerzo manual requerido por los equipos de comunicación.

### Alcance
- ✅ Solo genera contenido académico y universitario (validación incorporada)
- ✅ Publicación directa sin intervención manual en 5 plataformas
- ✅ Adaptación automática del contenido según cada red social
- ✅ Historial completo de publicaciones para auditoría
- ✅ Sistema multiusuario con autenticación segura

### Tecnologías Clave
- **OpenAI GPT**: Generación de texto natural y contextualizado
- **DALL-E 3**: Creación de imágenes únicas y relevantes
- **MoviePy**: Procesamiento de video para contenido dinámico
- **FastAPI**: Backend de alto rendimiento
- **Angular 18**: Frontend moderno y reactivo
- **PostgreSQL**: Almacenamiento confiable y escalable

### Casos de Uso
1. **Anuncios de eventos**: Congresos, seminarios, talleres
2. **Convocatorias**: Admisiones, becas, concursos
3. **Celebraciones**: Aniversarios, graduaciones, logros
4. **Noticias académicas**: Publicaciones, investigaciones, proyectos
5. **Información administrativa**: Matrículas, fechas importantes, cambios

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

---

**Desarrollado con dedicación para instituciones educativas** 🎓
