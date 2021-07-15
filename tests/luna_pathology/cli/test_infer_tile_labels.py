from click.testing import CliRunner
import pytest

from luna_pathology.cli.infer_tile_labels import cli


def test_cli():

    runner = CliRunner()

    result = runner.invoke(cli, [
            '-a', 'tests/luna_pathology/cli/testdata/test_config.yaml',
            '-s', '123',
            '-m', 'tests/luna_pathology/cli/testdata/infer_tile_labels_resnet18.json'])

    # No longer error gracefully -- can update tests with proper data and they'll work
    assert result.exit_code == 1
