from __future__ import annotations

import streamlit_app.theme as theme


class DummyContext:
    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[no-untyped-def]
        return False


class FakeStreamlit:
    def __init__(self) -> None:
        self.session_state: dict[str, str] = {}
        self.markdowns: list[str] = []
        self.buttons: list[dict[str, object]] = []

    def markdown(self, value: str, **_kwargs) -> None:
        self.markdowns.append(value)

    def columns(self, count: int, **_kwargs):  # type: ignore[no-untyped-def]
        return [DummyContext() for _ in range(count)]

    def button(self, label: str, **kwargs) -> None:
        self.buttons.append({"label": label, **kwargs})


def test_set_navigation_updates_session_state(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(theme, "st", fake_st)

    theme.set_navigation("KPIs")

    assert fake_st.session_state["dashboard_section_nav"] == "KPIs"


def test_render_story_nav_builds_navigation_buttons(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    fake_st.session_state["dashboard_section_nav"] = "Tempo"
    monkeypatch.setattr(theme, "st", fake_st)

    current = theme.render_story_nav()

    assert current == "Tempo"
    assert len(fake_st.buttons) == len(theme.NAVIGATION_OPTIONS)
    assert any(button["type"] == "primary" for button in fake_st.buttons)


def test_apply_theme_injects_css(monkeypatch) -> None:
    fake_st = FakeStreamlit()
    monkeypatch.setattr(theme, "st", fake_st)

    theme.apply_theme()

    assert any("<style>" in markdown for markdown in fake_st.markdowns)
    assert any(theme.APP_FONT in markdown for markdown in fake_st.markdowns)
