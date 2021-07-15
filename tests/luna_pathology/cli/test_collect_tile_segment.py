from click.testing import CliRunner

from luna_pathology.cli.collect_tile_segment import cli
import shutil, os

# @todo FIX: https://github.com/msk-mind-apps/luna-core/blob/main/luna_core/common/DataStore.py#L17
# def test_cli():
#
#     runner = CliRunner()
#     result = runner.invoke(cli, [
#         '-a', 'tests/luna_pathology/cli/testdata/test_config.yaml',
#         '-s', '123',
#         '-m', 'tests/luna_pathology/cli/testdata/collect_tile_results.json'])
#
#     assert result.exit_code == 0
#     assert os.path.exists('tests/luna_pathology/cli/testdata/data/test/slides/ovarian_clf_v1/123.parquet')
#
#     # cleanup
#     shutil.rmtree('tests/luna_pathology/cli/testdata/data/test/slides/ovarian_clf_v1/')

