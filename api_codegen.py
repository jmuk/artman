#!/usr/bin/env python

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

"""CLI to execute pipeline of code generation.

This runs the pipeline tasks remotely by default and asks remote tasks
to load the pipeline configs there, instead of specifying the config
from the command line.

TODO: Currently this command assumes all service proto files and
Gapic YAML files are checked in to googleapis repository. We will
want to allow supplying those files from the command line instead.
"""


import argparse

from taskflow import engines
from pipeline.pipelines import pipeline_factory
from pipeline.utils import job_util


def main():
    parser = _CreateArgumentParser()
    flags = parser.parse_args()
    kwargs = {
        'language': flags.language,
        'api_version': flags.api,
        'client_type': flags.client_type,
        'reporoot': flags.reporoot,
    }
    pipeline = pipeline_factory.ConfigLoadingCodeGenerationPipeline(**kwargs)
    if flags.run_locally:
        engine = engines.load(pipeline.flow, engine='serial',
                              store=pipeline.kwargs)
        engine.run()
    else:
        job_util.post_remote_pipeline_job(pipeline)


def _CreateArgumentParser():
    parser = argparse.ArgumentParser(
        description='''CLI to execute pipeline of code generation.

        This runs the code generation pipeline with asking tasks to load the
        pipeline configs on their side. This helps remote execution, because the
        commandline users (you) don't have to bring the configuration files
        locally.''')

    parser.add_argument('--language', '-l', type=str,
                        help='The target programming language to be generated')
    parser.add_argument(
        '--api', '-a', type=str,
        help='The API name with version (e.g. logging/v2 or pubsub/v1)')
    parser.add_argument('--client_type', default='gapic', type=str,
                        choices=['gapic', 'grpc'],
                        help='The type of the client to be generated')
    parser.add_argument(
        '--reporoot', type=str, default='..',
        help='Change the path to find googleapis repository when specified')
    parser.add_argument(
        '--run_locally', action='store_true',
        help='For debug. When specified, run the pipeline on the local machine')
    return parser


if __name__ == "__main__":
  main()
