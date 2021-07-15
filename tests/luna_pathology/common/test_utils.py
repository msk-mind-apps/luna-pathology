from luna_core.common.config import ConfigSet
import luna_core.common.constants as const
from luna_pathology.common.utils import get_labelset_keys


def test_get_labelset_keys():

    cfg = ConfigSet(name=const.DATA_CFG,
                    config_file='tests/luna_pathology/common/testdata/point_geojson_config.yaml')

    res = get_labelset_keys()

    assert 1 == len(res)
    assert 'LYMPHOCYTE_DETECTION_LABELSET' == res[0]
