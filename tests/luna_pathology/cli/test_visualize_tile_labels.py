import shutil
from click.testing import CliRunner

from luna_pathology.cli.visualize_tile_labels import cli

#@todo https://github.com/msk-mind-apps/luna-core/blob/main/luna_core/common/DataStore.py#L17
# def test_cli():
#
#     runner = CliRunner()
#     result = runner.invoke(cli, [
#         '-a', 'tests/luna_pathology/cli/testdata/test_config.yaml',
#         '-s', '123',
#         '-m', 'tests/luna_pathology/cli/testdata/visualize_tile_labels.json'])
#
#     assert result.exit_code == 0
#     shutil.rmtree('tests/luna_pathology/cli/testdata/data/test/slides/123/test_visualize_tiles')
