import warnings

import plotly.graph_objects as go

import app.main as main


def test_dark_theme_covers_plotly_chart_families(monkeypatch) -> None:
    monkeypatch.setattr(main.st, "session_state", {"ui_dark_mode": True})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        figures = [
            go.Figure(go.Scatter(x=[1, 2], y=[2, 1])),
            go.Figure(go.Scatterpolar(r=[1, 2], theta=[0, 90])),
            go.Figure(go.Scatter3d(x=[0, 1], y=[0, 1], z=[1, 0])),
            go.Figure(go.Scatterternary(a=[0.2, 0.5], b=[0.3, 0.2], c=[0.5, 0.3])),
            go.Figure(go.Scattergeo(lat=[48.8], lon=[2.3])),
            go.Figure(go.Scattermapbox(lat=[48.8], lon=[2.3])),
            go.Figure(go.Scattermap(lat=[48.8], lon=[2.3])),
            go.Figure(go.Heatmap(z=[[1, 2], [3, 4]], showscale=True)),
            go.Figure(
                go.Sankey(
                    node={"label": ["A", "B"]},
                    link={"source": [0], "target": [1], "value": [1]},
                )
            ),
            go.Figure(go.Indicator(mode="gauge+number", value=42)),
        ]

        for figure in figures:
            themed = main._apply_dark_plotly_layout(figure)
            assert themed.layout.paper_bgcolor == "#22242a"
            assert themed.layout.plot_bgcolor == "#292b30"
            assert themed.layout.font.color == "#bfbfbf"


def test_generated_chart_controls_and_shapes_follow_dark_theme(monkeypatch) -> None:
    monkeypatch.setattr(main.st, "session_state", {"ui_dark_mode": True})
    figure = go.Figure(go.Scatter(x=[1, 2], y=[1, 2]))
    figure.update_layout(
        template=main._plotly_template(),
        plot_bgcolor=main._plotly_plot_bgcolor(),
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": "Exemple",
                        "method": "update",
                        "args": [{"visible": [True]}],
                    }
                ],
                "bgcolor": "rgba(255,255,255,0.90)",
            }
        ],
        shapes=[
            {
                "type": "rect",
                "x0": 1,
                "x1": 2,
                "y0": 1,
                "y1": 2,
                "fillcolor": "#fffdf7",
            }
        ],
    )

    themed = main._apply_dark_plotly_layout(figure)

    assert main._plotly_template() == "plotly_dark"
    assert themed.layout.updatemenus[0].bgcolor == "#3a3b40"
    assert themed.layout.shapes[0].fillcolor == "#3a3b40"


def test_dark_theme_compacts_and_moves_visible_legends_outside_plot(monkeypatch) -> None:
    monkeypatch.setattr(main.st, "session_state", {"ui_dark_mode": True})
    figure = go.Figure(
        [
            go.Scatter(x=[1, 2], y=[1, 2], name="Série observée"),
            go.Scatter(x=[1, 2], y=[2, 1], name="Série prédite"),
        ]
    )
    figure.update_layout(legend={"x": 0.98, "y": 0.98})

    themed = main._apply_dark_plotly_layout(figure)

    assert themed.layout.legend.font.size == 9
    assert themed.layout.legend.x == 1.02
    assert themed.layout.legend.xanchor == "left"
    assert themed.layout.legend.y == 1.0
    assert themed.layout.margin.r >= 105


def test_dark_theme_reserves_space_for_horizontal_legends(monkeypatch) -> None:
    monkeypatch.setattr(main.st, "session_state", {"ui_dark_mode": True})
    figure = go.Figure(
        [
            go.Bar(x=["A"], y=[1], name="Groupe A"),
            go.Bar(x=["A"], y=[2], name="Groupe B"),
        ]
    )
    figure.update_layout(legend={"orientation": "h", "y": 1.02})

    themed = main._apply_dark_plotly_layout(figure)

    assert themed.layout.legend.orientation == "h"
    assert themed.layout.legend.yanchor == "bottom"
    assert themed.layout.margin.t >= 92


def test_generated_chart_template_stays_light_in_light_mode(monkeypatch) -> None:
    monkeypatch.setattr(main.st, "session_state", {"ui_dark_mode": False})

    assert main._plotly_template() == "plotly_white"
    assert main._plotly_plot_bgcolor() == "#fbfcff"
