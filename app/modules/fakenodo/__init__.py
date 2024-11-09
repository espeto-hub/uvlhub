from core.blueprints.base_blueprint import BaseBlueprint
from app.modules.zenodo import zenodo_bp

fakenodo_bp = BaseBlueprint('fakenodo', __name__, template_folder='templates')
