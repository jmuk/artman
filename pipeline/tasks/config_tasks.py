# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tasks related to read config data from local files."""

import os

from pipeline.utils import config_util
from pipeline.tasks import task_base


class ConfigReadTask(task_base.TaskBase):
    """A task to read pipeline configs from local files.

    As the result, the pipeline arguments will be loaded from the local
    environment of the task execution instead of passing from the commandline.
    This separation is helpful when the pipeline tasks run in remote clusters.
    """

    default_provides = set(['src_proto_path', 'import_proto_path',
                            'toolkit_path', 'output_dir', 'service_yaml',
                            'gapic_language_yaml', 'gapic_api_yaml',
                            'auto_merge', 'auto_resolve', 'ignore_base',
                            'final_repo_dir', 'api_name'])

    def execute(self, reporoot, language, api_version):
        config_base = os.path.join(reporoot, 'googleapis', 'gapic')
        language_config = os.path.join(config_base, 'lang', 'common.yaml')
        gapic_config = os.path.join(config_base, 'api', 'artman_common.yaml')
        api_name = api_version.split('/')[0]
        repl_vars = {
            'REPOROOT': reporoot,
            'API_VERSION': api_version,
            'API_NAME': api_name,
        }
        data = {'api_name': api_name}
        data.update(config_util.load_config(
            gapic_config, ['common', language], repl_vars))
        data.update(config_util.load_config(
            language_config, ['default', language], repl_vars))
        return data
