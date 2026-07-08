"""Tests for SRIE Engine Studio core modules."""
import pytest
import json
from datetime import datetime, timezone


class TestIndustryPacks:
    
    def test_all_packs_exist(self):
        from modules.studio.industry_packs import INDUSTRY_PACKS, list_industries
        assert len(INDUSTRY_PACKS) == 4
        assert 'transporte' in INDUSTRY_PACKS
        assert 'psicologia' in INDUSTRY_PACKS
        assert 'construccion' in INDUSTRY_PACKS
        assert 'sector_publico' in INDUSTRY_PACKS
    
    def test_list_industries(self):
        from modules.studio.industry_packs import list_industries
        industries = list_industries()
        assert len(industries) == 4
        for ind in industries:
            assert 'id' in ind
            assert 'nombre' in ind
            assert 'icono' in ind
    
    def test_get_prompt_extension(self):
        from modules.studio.industry_packs import get_industry_prompt_extension
        ext = get_industry_prompt_extension('transporte')
        assert 'Transporte' in ext
        assert 'KPIs' in ext
    
    def test_get_unknown_industry(self):
        from modules.studio.industry_packs import get_industry_prompt_extension, get_industry_pack
        assert get_industry_pack('unknown') is None
        assert get_industry_prompt_extension('unknown') == ''


class TestCodeGenerator:
    
    def test_generate_models(self):
        from modules.studio.code_generator import generate_models_py
        modelo = {
            'entidades': [
                {
                    'nombre': 'Cliente',
                    'atributos': [
                        {'nombre': 'id', 'tipo': 'UUID', 'pk': True, 'descripcion': 'ID unico'},
                        {'nombre': 'nombre', 'tipo': 'VARCHAR(255)', 'descripcion': 'Nombre'},
                    ],
                    'relaciones': [
                        {'entidad_destino': 'Factura', 'tipo': '1:N', 'descripcion': 'Tiene facturas'}
                    ]
                }
            ]
        }
        codigo = generate_models_py(modelo)
        assert 'class Cliente' in codigo
        assert 'BaseModel' in codigo
        assert 'facturas' in codigo
        assert 'id' in codigo
        assert 'nombre' in codigo
    
    def test_generate_empty_models(self):
        from modules.studio.code_generator import generate_models_py
        codigo = generate_models_py({'entidades': []})
        assert 'Modelos generados' in codigo
    
    def test_generate_routes(self):
        from modules.studio.code_generator import generate_routes_py
        api = {
            'endpoints': [
                {'metodo': 'GET', 'ruta': '/api/clientes', 'descripcion': 'Listar', 'auth': True},
                {'metodo': 'POST', 'ruta': '/api/clientes', 'descripcion': 'Crear', 'auth': True},
            ],
            'integraciones': [{'sistema': 'Stripe', 'tipo': 'pagos'}]
        }
        codigo = generate_routes_py(api)
        assert 'def get_api_clientes' in codigo
        assert 'def post_api_clientes' in codigo
        assert 'login_required' in codigo
    
    def test_generate_requirements(self):
        from modules.studio.code_generator import generate_requirements
        api = {'integraciones': [{'sistema': 'Stripe', 'tipo': 'pagos'}]}
        reqs = generate_requirements(api)
        assert 'Flask' in reqs
        assert 'stripe' in reqs
    
    def test_generate_project_zip(self):
        from modules.studio.code_generator import generate_project_zip
        buffer = generate_project_zip(
            {'entidades': []},
            {'endpoints': [], 'integraciones': []},
            {'stack': []},
            'test-project'
        )
        assert buffer.read(4) == b'PK\x03\x04'  # ZIP magic number


class TestSRIEMapper:
    
    def test_mapping_rules_exist(self):
        from modules.studio.srie_mapper import get_all_soluciones
        soluciones = get_all_soluciones()
        assert len(soluciones) >= 10
        nombres = [s['modulo'] for s in soluciones]
        assert 'StoneCRM' in nombres
        assert 'StoneDocs' in nombres
        assert 'StoneFlow' in nombres
    
    def test_map_empty_brechas(self):
        from modules.studio.srie_mapper import map_brechas_to_soluciones
        result = map_brechas_to_soluciones([], None)
        assert result == []


class TestAIPrompts:
    
    def test_capas_exist(self):
        from modules.studio.ai_prompts import FASES
        assert len(FASES) == 4
        assert FASES[0]['nombre'] == 'Entendamos su negocio'
        assert FASES[3]['nombre'] == 'Entorno y futuro'
    
    def test_get_system_prompt(self):
        from modules.studio.ai_prompts import get_system_prompt
        prompt = get_system_prompt(0, 'contexto de prueba', 2)
        assert 'FASE ACTUAL' in prompt
        assert 'Entendamos su negocio' in prompt
        assert 'contexto de prueba' in prompt
    
    def test_prompt_has_evidence_framework(self):
        from modules.studio.ai_prompts import get_system_prompt
        prompt = get_system_prompt(1, '', 1)
        assert 'confirmado' in prompt
        assert 'inferido' in prompt
        assert 'hipotesis' in prompt


class TestConsultoriaModel:
    
    def test_create_consultoria(self, app):
        with app.app_context():
            from core import db
            from core.models import Client
            from core.models.consultoria import Consultoria
            db.create_all()
            
            client = Client(company_name='TestM', contact_name='TM', contact_email='tm@test.com')
            db.session.add(client)
            db.session.flush()
            
            cons = Consultoria(cliente_id=client.id, estado='borrador', industria='transporte')
            db.session.add(cons)
            db.session.commit()
            
            assert cons.id is not None
            assert cons.industria == 'transporte'
            assert cons.estado == 'borrador'
    
    def test_create_mensaje(self, app):
        with app.app_context():
            from core import db
            from core.models import Client
            from core.models.consultoria import Consultoria, ConsultoriaMensaje
            db.create_all()
            
            client = Client(company_name='Test', contact_name='T', contact_email='t@t.com')
            db.session.add(client)
            db.session.flush()
            cons = Consultoria(cliente_id=client.id)
            db.session.add(cons)
            db.session.commit()
            
            msg = ConsultoriaMensaje(consultoria_id=cons.id, rol='ia', contenido='Hola')
            db.session.add(msg)
            db.session.commit()
            
            assert msg.id is not None
            assert msg.rol == 'ia'
            assert msg.contenido == 'Hola'


class TestMagicLink:
    
    def test_create_magic_link(self, app):
        with app.app_context():
            from core import db
            from core.models import Client
            from core.models.consultoria import Consultoria
            from core.models.magic_link import MagicLink
            db.create_all()
            
            client = Client(company_name='Test3', contact_name='T3', contact_email='t3@test.com')
            db.session.add(client)
            db.session.flush()
            cons = Consultoria(cliente_id=client.id)
            db.session.add(cons)
            db.session.commit()
            
            link = MagicLink.create(cons.id, 'test@test.com')
            assert link.token is not None
            assert link.email == 'test@test.com'
            assert link.is_valid() == True


class TestMarketplace:

    def test_list_industries_marketplace(self):
        from modules.studio.industry_packs import list_industries
        industries = list_industries()
        assert len(industries) == 4
        assert any(i['id'] == 'transporte' for i in industries)

    def test_apply_industry_to_consultoria(self, app):
        with app.app_context():
            from core import db
            from core.models import Client
            from core.models.consultoria import Consultoria
            db.create_all()
            c = Client(company_name='Mkt', contact_name='M', contact_email='mkt@test.com')
            db.session.add(c)
            db.session.flush()
            cons = Consultoria(cliente_id=c.id)
            db.session.add(cons)
            db.session.commit()
            assert cons.industria is None or cons.industria == 'general'
            cons.industria = 'construccion'
            db.session.commit()
            assert cons.industria == 'construccion'

    def test_marketplace_routes_exist(self, app):
        with app.app_context():
            rules = [str(r.rule) for r in app.url_map.iter_rules() if '/marketplace' in str(r.rule)]
            assert len(rules) >= 3


class TestTeams:

    def test_create_team_model(self, app):
        with app.app_context():
            from core import db
            from core.models.team import Team, TeamMember
            from core.models.admin_user import AdminUser
            db.create_all()
            
            admin = AdminUser(email='team@test.com', full_name='Team Test', role='super_admin')
            admin.set_password('test123')
            db.session.add(admin)
            db.session.flush()
            
            team = Team(name='Test Team', description='Test', created_by=admin.id)
            db.session.add(team)
            db.session.flush()
            
            member = TeamMember(team_id=team.id, user_id=admin.id, role='admin')
            db.session.add(member)
            db.session.commit()
            
            assert team.name == 'Test Team'
            assert len(team.members) == 1
            assert team.members[0].role == 'admin'

    def test_team_routes_exist(self, app):
        with app.app_context():
            rules = [str(r.rule) for r in app.url_map.iter_rules() if '/teams' in str(r.rule)]
            assert len(rules) >= 4


class TestAnalytics:

    def test_analytics_routes_exist(self, app):
        with app.app_context():
            rules = [str(r.rule) for r in app.url_map.iter_rules() if '/analytics' in str(r.rule)]
            assert len(rules) >= 2

    def test_analytics_data_api(self, app):
        with app.app_context():
            from modules.analytics.routes import analytics_bp
            assert analytics_bp is not None


class TestAutoDeploy:

    def test_generate_docker_compose(self):
        from modules.studio.code_generator import generate_docker_compose
        dc = generate_docker_compose({'stack': []}, 'test')
        assert 'web' in dc and 'db' in dc and 'postgres' in dc

    def test_generate_github_actions(self):
        from modules.studio.code_generator import generate_github_actions
        ga = generate_github_actions('test')
        assert 'CI/CD' in ga and 'pytest' in ga

    def test_generate_env_example(self):
        from modules.studio.code_generator import generate_env_example
        env = generate_env_example()
        assert 'DATABASE_URL' in env

    def test_generate_readme(self):
        from modules.studio.code_generator import generate_readme
        readme = generate_readme('Test', {'stack': [{'capa': 'backend', 'tecnologia': 'Flask'}]})
        assert 'Test' in readme and 'Flask' in readme

    def test_generate_full_project_zip(self):
        from modules.studio.code_generator import generate_full_project
        buffer = generate_full_project(
            {'entidades': [{'nombre': 'E1', 'atributos': [{'nombre': 'id', 'tipo': 'UUID', 'pk': True}], 'relaciones': []}]},
            {'endpoints': [], 'integraciones': []},
            {'stack': []},
            'test',
        )
        assert buffer.read(4) == b'PK\x03\x04'

    def test_deploy_route_exists(self, app):
        with app.app_context():
            rules = [str(r.rule) for r in app.url_map.iter_rules() if 'generar-deploy' in str(r.rule)]
            assert len(rules) >= 1
