from textual.design import ColorSystem
from typing import Optional
from dataclasses import dataclass


@dataclass
class Colors:
    primary_darken_3: str
    primary_darken_2: str
    primary_darken_1: str
    primary: str
    primary_lighten_1: str
    primary_lighten_2: str
    primary_lighten_3: str
    secondary_darken_3: str
    secondary_darken_2: str
    secondary_darken_1: str
    secondary: str
    secondary_lighten_1: str
    secondary_lighten_2: str
    secondary_lighten_3: str
    primary_background_darken_3: str
    primary_background_darken_2: str
    primary_background_darken_1: str
    primary_background: str
    primary_background_lighten_1: str
    primary_background_lighten_2: str
    primary_background_lighten_3: str
    secondary_background_darken_3: str
    secondary_background_darken_2: str
    secondary_background_darken_1: str
    secondary_background: str
    secondary_background_lighten_1: str
    secondary_background_lighten_2: str
    secondary_background_lighten_3: str
    background_darken_3: str
    background_darken_2: str
    background_darken_1: str
    background: str
    background_lighten_1: str
    background_lighten_2: str
    background_lighten_3: str
    foreground_darken_3: str
    foreground_darken_2: str
    foreground_darken_1: str
    foreground: str
    foreground_lighten_1: str
    foreground_lighten_2: str
    foreground_lighten_3: str
    panel_darken_3: str
    panel_darken_2: str
    panel_darken_1: str
    panel: str
    panel_lighten_1: str
    panel_lighten_2: str
    panel_lighten_3: str
    boost_darken_3: str
    boost_darken_2: str
    boost_darken_1: str
    boost: str
    boost_lighten_1: str
    boost_lighten_2: str
    boost_lighten_3: str
    surface_darken_3: str
    surface_darken_2: str
    surface_darken_1: str
    surface: str
    surface_lighten_1: str
    surface_lighten_2: str
    surface_lighten_3: str
    warning_darken_3: str
    warning_darken_2: str
    warning_darken_1: str
    warning: str
    warning_lighten_1: str
    warning_lighten_2: str
    warning_lighten_3: str
    error_darken_3: str
    error_darken_2: str
    error_darken_1: str
    error: str
    error_lighten_1: str
    error_lighten_2: str
    error_lighten_3: str
    success_darken_3: str
    success_darken_2: str
    success_darken_1: str
    success: str
    success_lighten_1: str
    success_lighten_2: str
    success_lighten_3: str
    accent_darken_3: str
    accent_darken_2: str
    accent_darken_1: str
    accent: str
    accent_lighten_1: str
    accent_lighten_2: str
    accent_lighten_3: str
    text: str
    text_muted: str
    text_disabled: str


class ThemeMeta(type):

    __instance: Optional["Theme"] = None

    def __call__(cls):
        if not cls.__instance:
            cls.__instance = type.__call__(cls)
        return cls.__instance

    @property
    def system(cls) -> ColorSystem:
        return cls().get_system()

    @system.setter
    def system(cls, value: str):
        cls().set_theme(value)

    @property
    def colors(cls) -> Colors:
        return cls().get_colors()


class Theme(object, metaclass=ThemeMeta):
    DEFAULT_COLORS = {
        "dark": ColorSystem(
            primary="#004578",
            secondary="#ffa62b",
            warning="#ffa62b",
            error="#ba3c5b",
            success="#4EBF71",
            accent="#0178D4",
            dark=True,
        ),
        "light": ColorSystem(
            primary="#004578",
            secondary="#ffa62b",
            warning="#ffa62b",
            error="#ba3c5b",
            success="#4EBF71",
            accent="#0178D4",
            dark=False,
        ),
    }
    __theme: str = "dark"

    def __init__(self) -> None:
        self.__system = self.DEFAULT_COLORS[self.__theme]
        self.__colors = Colors(
            **{k.replace("-", "_"): v for k, v in self.__system.generate().items()}
        )

    def get_system(self) -> ColorSystem:
        return self.__system

    def set_theme(self, value: str):
        self.__theme = value
        self.__system = self.DEFAULT_COLORS[self.__theme]
        self.__colors = Colors(
            **{k.replace("-", "_"): v for k, v in self.__system.generate().items()}
        )

    def get_colors(self) -> Colors:
        return self.__colors
