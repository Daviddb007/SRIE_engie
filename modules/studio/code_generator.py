"""Code Generator — generates actual code from Constructor specs."""


def generate_models_py(modelo_datos: dict) -> str:
    """Generate SQLAlchemy models from data model specs."""
    lines = [
        '"""Modelos generados por SRIE Engine."""',
        'from core import db',
        'from core.models.base import BaseModel',
        '',
    ]
    for entidad in modelo_datos.get('entidades', []):
        nombre = entidad.get('nombre', 'Entidad')
        table = ''.join(f'_{c.lower()}' if c.isupper() else c for c in nombre).lower()
        lines.append(f'\nclass {nombre}(BaseModel):')
        lines.append(f"    __tablename__ = '{table}s'")
        lines.append('')
        for attr in entidad.get('atributos', []):
            attr_name = attr.get('nombre', 'id')
            attr_type = attr.get('tipo', 'String')
            is_pk = attr.get('pk', False)
            nullable = 'NOT NULL' if is_pk else 'nullable=True'
            col_type = _map_type(attr_type)
            pk_str = ', primary_key=True' if is_pk else ''
            desc = attr.get('descripcion', '')
            lines.append(f"    {attr_name} = db.Column(db.{col_type}{pk_str})  # {desc}")

        for rel in entidad.get('relaciones', []):
            dest = rel.get('entidad_destino', '')
            rel_type = rel.get('tipo', '')
            if rel_type == '1:N':
                lines.append(f"    {dest.lower()}s = db.relationship('{dest}', backref='{nombre.lower()}', lazy=True)")
            elif rel_type == 'N:M':
                lines.append(f"    {dest.lower()}s = db.relationship('{dest}', secondary='{nombre.lower()}_{dest.lower()}s', lazy=True)")

    return '\n'.join(lines)


def generate_routes_py(api_especs: dict) -> str:
    """Generate Flask route stubs from API specs."""
    lines = [
        '"""Rutas generadas por SRIE Engine."""',
        'from __future__ import annotations',
        'from flask import Blueprint, request, jsonify',
        "from flask_login import login_required",
        '',
        'bp = Blueprint("api", __name__, url_prefix="/api")',
        '',
    ]
    for ep in api_especs.get('endpoints', []):
        method = ep.get('metodo', 'GET').lower()
        route = ep.get('ruta', '/')
        desc = ep.get('descripcion', '')
        needs_auth = ep.get('auth', True)
        decorator = '@login_required\n' if needs_auth else ''

        lines.append(f'')
        lines.append(f'{decorator}@bp.route("{route}", methods=["{method.upper()}"])')
        lines.append(f'def {_route_to_func(route, method)}():')
        lines.append(f'    """{desc}"""')
        if method == 'get':
            lines.append(f'    return jsonify({{"message": "Listar {_route_to_func(route, method)}"}})')
        elif method == 'post':
            lines.append(f'    data = request.get_json()')
            lines.append(f'    return jsonify({{"message": "Crear", "data": data}}), 201')
        elif method in ('put', 'patch'):
            lines.append(f'    data = request.get_json()')
            lines.append(f'    return jsonify({{"message": "Actualizar", "data": data}})')
        elif method == 'delete':
            lines.append(f'    return jsonify({{"message": "Eliminado"}}), 204')
        lines.append('')

    return '\n'.join(lines)


def generate_dockerfile(arquitectura: dict) -> str:
    """Generate Dockerfile from architecture specs."""
    stack_info = {}
    for item in arquitectura.get('stack', []):
        stack_info[item.get('capa', '')] = item.get('tecnologia', '')

    lines = [
        'FROM python:3.11-slim',
        '',
        'WORKDIR /app',
        '',
        'COPY requirements.txt .',
        'RUN pip install --no-cache-dir -r requirements.txt',
        '',
        'COPY . .',
        '',
        f'EXPOSE 5000',
        '',
        'CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]',
        '',
    ]
    return '\n'.join(lines)


def generate_docker_compose(arquitectura: dict, project_name: str = 'srie-app') -> str:
    stack_info = {}
    for item in arquitectura.get('stack', []):
        stack_info[item.get('capa', '')] = item.get('tecnologia', '')
    
    services = {
        'web': {
            'build': '.',
            'ports': ['5000:5000'],
            'env_file': '.env',
            'depends_on': ['db'],
        },
        'db': {
            'image': 'postgres:15-alpine',
            'environment': ['POSTGRES_DB=${DB_NAME}', 'POSTGRES_USER=${DB_USER}', 'POSTGRES_PASSWORD=${DB_PASS}'],
            'volumes': ['pgdata:/var/lib/postgresql/data'],
            'ports': ['5432:5432'],
        },
    }
    
    needs_redis = any('redis' in str(item).lower() or 'cache' in str(item).lower() for item in arquitectura.get('stack', []))
    if needs_redis:
        services['redis'] = {'image': 'redis:7-alpine', 'ports': ['6379:6379']}
    
    lines = ['version: "3.8"', '', 'services:']
    for name, cfg in services.items():
        lines.append(f'  {name}:')
        for k, v in cfg.items():
            if isinstance(v, list):
                lines.append(f'    {k}:')
                for item in v:
                    lines.append(f'      - {item}')
            elif isinstance(v, dict):
                lines.append(f'    {k}:')
                for sk, sv in v.items():
                    lines.append(f'      {sk}: {sv}')
            else:
                lines.append(f'    {k}: {v}')
    lines.extend(['', 'volumes:', '  pgdata:'])
    return '\n'.join(lines)


def generate_github_actions(project_name: str = 'srie-app') -> str:
    return '''name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Render
        run: |
          curl -X POST "https://api.render.com/deploy/srv/${{ secrets.RENDER_SERVICE_ID }}"
'''


def generate_env_example() -> str:
    return '''# Database
DATABASE_URL=postgresql://user:password@localhost:5432/srie_db
DB_NAME=srie_db
DB_USER=user
DB_PASS=password

# Flask
FLASK_SECRET_KEY=change-this-to-a-random-secret
FLASK_DEBUG=0

# Optional
# OPENAI_API_KEY=sk-...
# MAIL_SERVER=smtp.example.com
'''


def generate_readme(project_name: str, arquitectura: dict) -> str:
    stack_info = []
    for item in arquitectura.get('stack', []):
        stack_info.append(f"- **{item.get('capa', '')}**: {item.get('tecnologia', '')}")

    return f'''# {project_name}

Proyecto generado por **SRIE Engine** — Stonelytics.

## Stack Tecnologico

{chr(10).join(stack_info) if stack_info else '- Flask 3.1 + SQLAlchemy'}

## Requisitos

- Python 3.11+
- Docker y Docker Compose (opcional)
- PostgreSQL

## Instalacion Local

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
python app.py
```

## Docker

```bash
docker-compose up --build
```

## Estructura

```
src/
  models.py    - Modelos de datos
  routes.py    - API endpoints
  app.py       - App factory
requirements.txt
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

## Tests

```bash
pytest
```
'''


def generate_full_project(datos_api, api_especs, arquitectura, project_name):
    """Generate complete project with all files."""
    import io, zipfile
    
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('src/__init__.py', '')
        zf.writestr('src/models.py', generate_models_py(datos_api))
        zf.writestr('src/routes.py', generate_routes_py(api_especs))
        zf.writestr('src/config.py', 'import os\n\nclass Config:\n    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret")\n    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")\n    SQLALCHEMY_TRACK_MODIFICATIONS = False\n')
        zf.writestr('src/app.py', 'from flask import Flask\nfrom src.config import Config\n\ndef create_app():\n    app = Flask(__name__)\n    app.config.from_object(Config)\n    return app\n\napp = create_app()\nif __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5000)\n')
        zf.writestr('Dockerfile', generate_dockerfile(arquitectura))
        zf.writestr('docker-compose.yml', generate_docker_compose(arquitectura, project_name))
        zf.writestr('requirements.txt', generate_requirements(api_especs))
        zf.writestr('.env.example', generate_env_example())
        zf.writestr('.github/workflows/ci.yml', generate_github_actions(project_name))
        zf.writestr('README.md', generate_readme(project_name, arquitectura))
        zf.writestr('.gitignore', 'venv/\n__pycache__/\n*.pyc\n.env\n*.db\n')
    buffer.seek(0)
    return buffer


def generate_requirements(api_especs: dict) -> str:
    """Generate requirements.txt based on API specs."""
    deps = [
        'Flask==3.1.1',
        'Flask-SQLAlchemy==3.1.1',
        'Flask-Login==0.6.3',
        'psycopg2-binary==2.9.9',
        'gunicorn==23.0.0',
        'python-dotenv==1.1.0',
    ]
    integrations = api_especs.get('integraciones', [])
    for integ in integrations:
        tipo = integ.get('tipo', '')
        if tipo == 'pagos':
            deps.append('stripe==10.0.0')
        elif tipo == 'email':
            deps.append('Flask-Mail==0.9.1')
    return '\n'.join(deps)


import io
import zipfile


def generate_project_zip(datos_api, api_especs, arquitectura, project_name):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('src/models.py', generate_models_py(datos_api))
        zf.writestr('src/routes.py', generate_routes_py(api_especs))
        zf.writestr('Dockerfile', generate_dockerfile(arquitectura))
        zf.writestr('requirements.txt', generate_requirements(api_especs))
        zf.writestr('README.md', f'# {project_name}\n\nProyecto generado por SRIE Engine.\n\n## Instalacion\n```\npip install -r requirements.txt\n```\n')
    buffer.seek(0)
    return buffer


def _map_type(tipo: str) -> str:
    mapping = {
        'UUID': 'String(36)',
        'VARCHAR': 'String(255)',
        'VARCHAR(255)': 'String(255)',
        'TEXT': 'Text',
        'INTEGER': 'Integer',
        'FLOAT': 'Float',
        'BOOLEAN': 'Boolean',
        'DATE': 'Date',
        'DATETIME': 'DateTime',
        'DECIMAL': 'Numeric(12,2)',
        'JSON': 'JSON',
    }
    return mapping.get(tipo.upper().split('(')[0], 'String(255)')


def _route_to_func(route: str, method: str) -> str:
    parts = route.strip('/').replace('/', '_').replace('-', '_').replace('<', '').replace('>', '')
    return f'{method}_{parts}' if parts else 'index'
