# Gastor API

API backend del ecosistema **Gastor**, desarrollada en **Flask** y desplegada mediante **Docker**, diseñada para gestionar gastos, movimientos financieros y archivos asociados (imágenes de comprobantes), con entornos separados DEV y PRD.

---

## 🚀 Características principales

- API REST construida con Flask

- Separación de entornos DEV y PRD

- Contenedorización con Docker / Docker Compose

- Integración con PostgreSQL

- Manejo de archivos (imágenes de gastos)

- Preparada para despliegue en CasaOS

- Compatible con Nginx Proxy Manager

---

## 🧱 Arquitectura general

GastorApp (Angular)  
↓  
Gastor API (Flask)  
↓  
Gastor DB (PostgreSQL)

Los archivos de imágenes se almacenan en el servidor mediante volúmenes Docker.

---

## 🐳 Docker y despliegue

El proyecto está preparado para ejecutarse mediante **Docker Compos**e, con perfiles separados para desarrollo y producción.

### Servicios

- gastor-api-dev → entorno de desarrollo

- gastor-api-prd → entorno de producción

### Puertos
| Entorno | Puerto host | Puerto contenedor |
|-------|-------------|-------------------|
| DEV   | 8001        | 8000              |
| PRD   | 8000        | 8000              |

---

## ▶️ Ejecución

### Producción
```bash
docker compose --profile prd up -d
```

### Desarrollo
```bash
docker compose --profile dev up -d
```

---

## 🔐 Variables de entorno

Cada entorno utiliza su propio archivo .env:

- dev.env

- prd.env

### Ejemplo de variables:

- FLASK_ENV=production
- DB_HOST=postgres
- DB_PORT=5432
- DB_NAME=gastor
- DB_USER=gastor_user
- DB_PASSWORD=********

---

## 🗂️ Manejo de archivos

Las imágenes de comprobantes se almacenan mediante volúmenes Docker:

```bash
volumes:
  - /DATA/File System/movimientos_fotos:/files/movimientos_fotos
```

Esto permite:

- Persistencia de archivos

- Separación del código y los datos

- Backups sencillos

---

## 🖥️ Despliegue en CasaOS

El proyecto incluye metadata para CasaOS mediante x-casaos:

```bash
x-casaos:
  icon: https://cdn-icons-png.flaticon.com/512/1493/1493169.png
  title: GastorApp - APIs
  description: API Flask para Gastor
```

Esto permite:

- Visualización con icono personalizado

- Gestión desde la UI de CasaOS

- Inicio y parada desde el dashboard

---

## 🔗 Acceso

- Producción: http://IP_SERVIDOR:8000

- Desarrollo: http://IP_SERVIDOR:8001

Normalmente expuesto mediante Nginx Proxy Manager o dominio interno.

## 📌 Tecnologías utilizadas

- Python

- Flask

- Docker

- Docker Compose

- PostgreSQL

- CasaOS

## 👤 Autor

Sebastián Sánchez  
Proyecto personal – Ecosistema Gastor
