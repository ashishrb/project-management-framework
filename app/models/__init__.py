# Models package for GenAI Metrics Dashboard

# Import all models to ensure they are registered with SQLAlchemy
from .main_tables import *
from .lookup_tables import *
from .junction_tables import *
from .project_detail_models import *
from .project_detail_lookups import *
