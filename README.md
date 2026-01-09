# TPV Portfolio Project

Este proyecto es un sistema de Terminal Punto de Venta (TPV) diseñado como una aplicación web moderna.

## Tecnologías y Librerías Utilizadas

### Backend
El backend está construido con **Python** utilizando el framework **FastAPI** para alta velocidad y rendimiento.

*   **FastAPI**: Framework web moderno y rápido para construir APIs.
*   **Uvicorn**: Servidor ASGI para producción.
*   **SQLAlchemy**: Toolkit SQL y ORM (Mapeo Objeto-Relacional) para la gestión de la base de datos (modo asíncrono).
*   **Aiosqlite**: Driver asíncrono para SQLite.
*   **Pydantic**: Validación de datos y gestión de configuraciones mediante modelos.
*   **Python-Jose**: Implementación de JOSE (Javascript Object Signing and Encryption) para generar y verificar tokens JWT.
*   **Passlib (con Bcrypt)**: Hashing seguro de contraseñas.
*   **Python-Dotenv**: Gestión de variables de entorno.

### Frontend
El frontend se ha desarrollado utilizando tecnologías web estándar sin dependencias de frameworks pesados, enfocándose en la simplicidad y el rendimiento.

*   **HTML5**: Estructura semántica.
*   **CSS3**: Estilos personalizados (Variables CSS, Flexbox, Grid).
*   **JavaScript (Vanilla)**: Lógica del cliente y comunicación asíncrona con la API.

### Base de Datos
*   **SQLite**: Base de datos relacional ligera y sin servidor, ideal para desarrollo y despliegue sencillo.
