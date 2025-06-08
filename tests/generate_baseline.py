import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cv_generator import CVGenerator
from tests.ascii_utils import pdf_to_ascii


def main():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'cv_data_example.json')
    output_pdf = os.path.join(os.path.dirname(__file__), 'expected', 'tmp_baseline.pdf')

    generator = CVGenerator()
    generator.create_cv(
        data_path=data_path,
        output_path=output_pdf,
        template_name='minimal'
    )

    ascii_text = pdf_to_ascii(output_pdf)
    expected_path = os.path.join(os.path.dirname(__file__), 'expected', 'minimal_cv_ascii.txt')
    with open(expected_path, 'w') as fh:
        fh.write(ascii_text)

    os.remove(output_pdf)
    print(f'Baseline updated: {expected_path}')


if __name__ == "__main__":
    main()
