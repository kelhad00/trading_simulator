"""The app finds the same data folder whatever folder it is started from."""
import os
import subprocess
import sys

from conftest import ROOT


def data_path_when_started_from(folder):
    code = f"import sys; sys.path.insert(0, {ROOT!r}); from trade.defaults import defaults as d; print(d.data_path)"
    return subprocess.run([sys.executable, "-c", code], cwd=folder, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_data_folder_is_next_to_the_app_code(tmp_path):
    expected = os.path.join(ROOT, "data")
    for folder in (os.path.join(ROOT, "trade"), ROOT, str(tmp_path)):
        assert os.path.normcase(data_path_when_started_from(folder)) == os.path.normcase(expected)
