from pathlib import Path
import jinja2

templates_dir = Path(__file__).parent.parent / "templates"

templates_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
