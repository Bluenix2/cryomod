from wumpy.interactions import InteractionApp

from .cases import cases as cases_cmd


def add_commands(app: InteractionApp) -> None:
    app.add_command(cases_cmd)
