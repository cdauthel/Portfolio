import app.main as main


def test_filter_rerun_restores_stable_page(monkeypatch) -> None:
    state = {
        "menu_section": "Analyse exploratoire",
        "submenu_Machine Learning": "Apprentissage non supervisé",
        "_stable_menu_section": "Machine Learning",
        "_stable_subpage": "Apprentissage supervisé",
    }
    monkeypatch.setattr(main.st, "session_state", state)

    main._restore_navigation_after_non_nav_rerun(list(main.SECTIONS))

    assert state["menu_section"] == "Machine Learning"
    assert state["submenu_Machine Learning"] == "Apprentissage supervisé"


def test_explicit_sidebar_and_subpage_navigation_update_stable_target(monkeypatch) -> None:
    state = {
        "menu_section": "Accueil et Profil",
        "subpage_by_section": {
            "Assistant IA": "RAG",
            "Machine Learning": "Apprentissage supervisé",
        },
    }
    monkeypatch.setattr(main.st, "session_state", state)

    main._activate_sidebar_section("Assistant IA")
    assert state["_stable_menu_section"] == "Assistant IA"
    assert state["_stable_subpage"] == "RAG"

    state["submenu_Machine Learning"] = "Apprentissage par renforcement"
    main._mark_explicit_subpage_navigation("Machine Learning")
    assert state["_stable_menu_section"] == "Machine Learning"
    assert state["_stable_subpage"] == "Apprentissage par renforcement"


def test_summary_pending_navigation_is_not_overridden(monkeypatch) -> None:
    state = {
        "menu_section": "Machine Learning",
        "submenu_Machine Learning": "Apprentissage supervisé",
        "_stable_menu_section": "Machine Learning",
        "_stable_subpage": "Apprentissage supervisé",
        "pending_navigation": {
            "section": "Accueil et Profil",
            "subpage": "Profil et CV",
        },
    }
    monkeypatch.setattr(main.st, "session_state", state)

    main._restore_navigation_after_non_nav_rerun(list(main.SECTIONS))

    assert state["menu_section"] == "Machine Learning"
    assert state["pending_navigation"]["subpage"] == "Profil et CV"
