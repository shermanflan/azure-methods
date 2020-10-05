

from utility import (AZ_SUBSCRIPTION, AZ_RESOURCE_GROUP,
                     AZ_LOG_WORKSPACE, DIAGNOSTIC_NAME)
from utility.cmd import (get_by_tag, is_monitored,
                         add_diagnostic, remove_diagnostic)


def test_filter_tag():
    """
    Test filtering resources by tag.

    :return: None
    """
    resources = get_by_tag(subscription=AZ_SUBSCRIPTION,
                           resource_group=AZ_RESOURCE_GROUP,
                           tag_name='auto-monitor',
                           tag_value='True')

    assert len(resources) == 2

    resources = get_by_tag(subscription=AZ_SUBSCRIPTION,
                           resource_group=AZ_RESOURCE_GROUP,
                           tag_name='auto-monitor',
                           tag_value='False')

    assert len(resources) == 1


def test_is_monitored():
    """
    Verify audit verify.

    :return:
    """
    resources = get_by_tag(subscription=AZ_SUBSCRIPTION,
                           resource_group=AZ_RESOURCE_GROUP,
                           tag_name='auto-monitor')

    filtered = [rid for rid, _ in resources
                if not is_monitored(DIAGNOSTIC_NAME, rid)]

    assert len(resources) == 3 and len(filtered) == 1
