import jinja2

template_loader = jinja2.PackageLoader('hammercloud', 'templates')
env = jinja2.Environment(loader=template_loader)
