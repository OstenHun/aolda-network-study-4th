import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('public_content_builder', ROOT / 'tools/build-site.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PublicContentBoundary(unittest.TestCase):
    def test_private_context_rejected_in_markdown_and_html(self):
        for sample in (
            '주간 기록 (진행자 보관 자료)',
            '<small>(팀 내부 안내)</small>',
            '## 핵심 정리 적용 — 2026-10-15',
            '<p>상태: <strong>draft</strong></p>',
            '참가자 8명 모두 수행했다.',
            '공통 로그인 안내',
            '<p>ubuntu 계정에 비밀번호를 입력한다.</p>',
            '<p>현재&#32;적용</p>',
            '팀별 목·금 오프라인은 확정했고 장소는 확인한다.',
            '인당 VM 두 대 사용 가능은 사용자 제공 조건이다.',
        ):
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                builder.check_learner_context(sample)

    def test_teaching_examples_and_source_provenance_remain_valid(self):
        builder.check_learner_context(
            '확인일: 2026-10-16. Ubuntu 예제 VM의 192.0.2.10은 설명용 주소다. '
            '셸 A와 B에서 관찰하고 본인에게 허용된 인증 방식을 사용한다. '
            '제공 예제 분석과 본인 직접 실행을 구분한다.'
        )

    def test_public_sources_and_teaching_capture_pass(self):
        self.assertGreater(builder.check_public_sources(), 0)

    def test_assembled_output_rejected_before_dist_is_written(self):
        for name, text in (
            ('index.html', '<main>사용자 요청으로 반영했다.</main>'),
            ('materials/lesson.html', '<nav>주간 기록 (팀 내부 안내)</nav>'),
            ('materials/search.html', '<script type="application/json">{"title":"현재 적용"}</script>'),
            ('materials/LESSON.md', '# 안내\n\n참가자 8명 모두 수행했다.'),
        ):
            with self.subTest(name=name), patch.object(builder, 'check_public_sources', return_value=0), \
                    patch.object(builder, 'make_payload', return_value={name: text.encode('utf-8')}), \
                    patch.object(builder, 'generated_folder') as output:
                with self.assertRaisesRegex(ValueError, name):
                    builder.build()
                output.assert_not_called()

    def test_output_allows_source_dates_and_generic_examples(self):
        builder.validate_public_output({
            'materials/lesson.html': '<p>공식 출처 확인일: 2026-10-16. 예제는 본인 직접 관찰과 구분한다.</p>'.encode('utf-8'),
            'materials/LESSON.md': '# 주소 예제\n\n192.0.2.10은 설명용 주소다.'.encode('utf-8'),
        })


if __name__ == '__main__':
    unittest.main()
