import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cv_generator import CVGenerator
from tests.ascii_utils import compare_with_baseline


def test_generate_pdf(tmp_path):
    data_path = os.path.join('cv_data_example.json')
    output_file = tmp_path / 'test_cv.pdf'

    generator = CVGenerator()
    generator.create_cv(
        data_path=data_path,
        output_path=str(output_file),
        template_name='minimal'
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    baseline = os.path.join('tests', 'expected', 'minimal_cv_ascii.txt')
    compare_with_baseline(str(output_file), baseline)
