from pathlib import Path
import py_compile


def test_streamlit_app_syntax() -> None:
    app_path = Path("app/main.py")
    assert app_path.exists()
    py_compile.compile(str(app_path), doraise=True)
