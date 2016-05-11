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

"""Factory function that recreates pipeline based on pipeline name and
kwargs."""

from pipeline.pipelines import pipeline_base
# These are required to list the subclasses of pipeline_base
from pipeline.pipelines import sample_pipeline  # noqa
from pipeline.pipelines import code_generation_pipeline  # noqa
from pipeline.tasks import config_tasks
from pipeline.utils import pipeline_util
from taskflow.patterns import linear_flow


def make_pipeline_flow(pipeline_name, **kwargs):
    """Factory function to make a GAPIC pipeline.

    Because the GAPIC pipeline is using OpenStack Taskflow, this factory
    function is expected to be a function (or staticmethod) which is
    reimportable (aka has a well defined name that can be located by the
    __import__ function in python, this excludes lambda style functions and
    instance methods). The factory function name will be saved into the
    logbook, and it will be imported and called to create the workflow objects
    (or recreate it if resumption happens).  This allows for the pipeline to be
    recreated if and when that is needed (even on remote machines, as long as
    the reimportable name can be located).

    """
    return make_pipeline(pipeline_name, **kwargs).flow


def make_pipeline(pipeline_name, **kwargs):
    for cls in _rec_subclasses(pipeline_base.PipelineBase):
        if cls.__name__ == pipeline_name:
            print("Create %s instance." % pipeline_name)
            return cls(**kwargs)
    raise ValueError("Invalid pipeline name: %s" % pipeline_name)


def _rec_subclasses(cls):
    """Returns all recursive subclasses of a given class (i.e., subclasses,
    sub-subclasses, etc.)"""
    subclasses = []
    if cls.__subclasses__():
        for subcls in cls.__subclasses__():
            subclasses.append(subcls)
            subclasses += _rec_subclasses(subcls)
    return subclasses


class ConfigLoadingCodeGenerationPipeline(pipeline_base.PipelineBase):
    """The pipeline which loads the config on the task execution environment.

    This fits well to execute tasks remotely, so local commandline users don't
    have to set up the pipeline configs.
    """

    def __init__(self, **kwargs):
        super(ConfigLoadingCodeGenerationPipeline, self).__init__(**kwargs)

    def do_build_flow(self, **kwargs):
        flow = linear_flow.Flow('config-loading-codegen')
        flow.add(config_tasks.ConfigReadTask('ConfigReader', inject=kwargs))
        pipeline_name = self.get_pipeline_prefix(**kwargs) + 'ClientPipeline'
        kwargs['suppress_validate_kwargs'] = True
        pipeline = make_pipeline(pipeline_name, **kwargs)
        flow.add(pipeline.flow)
        return flow

    def get_pipeline_prefix(self, **kwargs):
        language_prefix = kwargs['language']
        if language_prefix == 'csharp':
            language_prefix = 'CSharp'
        else:
            language_prefix = language_prefix.capitalize()
        type_prefix = kwargs['client_type'].capitalize()
        return language_prefix + type_prefix

    def validate_kwargs(self, **kwargs):
        pipeline_util.validate_exists(
            ['language', 'api_version', 'client_type', 'reporoot'], **kwargs)
