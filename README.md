# TPV Project (Point of Sale)

## Descripción General
Este proyecto es un sistema de Terminal Punto de Venta (TPV) diseñado para gestionar ventas, productos y empleados. Está construido con una arquitectura moderna que separa el backend del frontend.

## Arquitectura

### Backend
- **Framework**: FastAPI (Python).
- **Base de Datos**: SQLite (para desarrollo/MVP), gestionada con SQLAlchemy.
- **Autenticación**: JWT (JSON Web Tokens) para seguridad.
- **Estructura**: Modular, separando rutas, modelos, esquemas y lógica de negocio (CRUD).

### Frontend
- **Tecnologías**: HTML5, CSS3, JavaScript (Vanilla).
- **Diseño**: Interfaz limpia y responsiva.
- **Comunicación**: Fetch API para interactuar con el backend.

## Estructura del Proyecto

```
Tpv/
├── app/
│   ├── auth/           # Módulo de autenticación (Login, Registro, JWT)
│   ├── products/       # Gestión de productos (CRUD)
│   ├── sales/          # Gestión de ventas y tickets
│   ├── static/         # Archivos estáticos (JS, CSS, HTML)
│   ├── db.py           # Configuración de la base de datos
│   ├── main.py         # Punto de entrada de la aplicación FastAPI
│   └── ...
├── tpv.db              # Archivo de base de datos SQLite
├── requirements.txt    # Dependencias de Python
└── README.md           # Este archivo
```

## Instalación y Configuración

1. **Clonar el repositorio** (si aplica) o navegar a la carpeta del proyecto.

2. **Crear un entorno virtual** (recomendado):
   ```bash
   python -m venv .venv
   # Activar en Windows:
   .venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicializar la base de datos**:
   (Si es la primera vez)
   ```bash
   python app/create_db.py
   ```

## Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`.

## Uso

1. Abrir el navegador en `http://127.0.0.1:8000`.
2. Registrar un usuario (si no existe) o iniciar sesión.
3. Gestionar productos y realizar ventas.
