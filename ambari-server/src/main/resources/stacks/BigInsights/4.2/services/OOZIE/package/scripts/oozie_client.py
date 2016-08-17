#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
from resource_management import *
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import iop_select

from oozie import oozie
from oozie_service import oozie_service


class OozieClient(Script):

  def get_stack_to_component(self):
    return {"BigInsights": "oozie-client"}

  def install(self, env):
    self.install_packages(env)
    self.configure(env)


  def configure(self, env):
    import params
    env.set_params(params)

    oozie(is_server=False)

  def status(self, env):
    raise ClientComponentHasNoStatus()


  def pre_upgrade_restart(self, env, upgrade_type=None):
    import params
    env.set_params(params)

    # this function should not execute if the version can't be determined or
    # is not at least IOP 4.0.0.0
    if not params.version or compare_versions(format_hdp_stack_version(params.version), '4.0.0.0') < 0:
      return

    Logger.info("Executing Oozie Client Rolling Upgrade pre-restart")
    conf_select.select(params.stack_name, "oozie", params.version)
    iop_select.select("oozie-client", params.version)
    #Execute(format("iop-select set oozie-client {version}"))

  # We substitute some configs (oozie.authentication.kerberos.principal) before generation (see oozie.py and params.py).
  # This function returns changed configs (it's used for config generation before config download)
  def generate_configs_get_xml_file_content(self, filename, dictionary):
    if dictionary == 'oozie-site':
      import params
      config = self.get_config()
      return {'configurations': params.oozie_site,
              'configuration_attributes': config['configuration_attributes'][dictionary]}
    else:
      return super(OozieClient, self).generate_configs_get_xml_file_content(filename, dictionary)

if __name__ == "__main__":
  OozieClient().execute()