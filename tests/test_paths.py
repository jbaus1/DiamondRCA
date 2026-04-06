from diamond_rca.paths import (
    EXTERNAL_DATA_DIR,
    FIGURES_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    ensure_project_dirs,
)


def test_ensure_project_dirs_creates_directories():
    ensure_project_dirs()

    assert RAW_DATA_DIR.exists()
    assert PROCESSED_DATA_DIR.exists()
    assert EXTERNAL_DATA_DIR.exists()
    assert FIGURES_DIR.exists()
