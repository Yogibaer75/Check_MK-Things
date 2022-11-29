#!/usr/bin/env python3
from cmk.gui.plugins.metrics.utils import check_metrics
from cmk.gui.plugins.metrics.translation import df_translation

check_metrics["check_mk-prism_host_usage"] = df_translation
check_metrics["check_mk-prism_containers"] = df_translation
check_metrics["check_mk-prism_storage_pools"] = df_translation
