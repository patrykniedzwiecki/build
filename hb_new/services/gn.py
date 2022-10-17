#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import sys
import os
from enum import Enum

from containers.status import throw_exception
from exceptions.ohosException import OHOSException
from services.interface.buildFileGeneratorInterface import BuildFileGeneratorInterface
from resources.config import Config
from util.systemUtil import SystemUtil
from util.ioUtil import IoUtil
from util.logUtil import LogUtil


class CMDTYPE(Enum):
    GEN = 1
    PATH = 2
    DESC = 3
    LS = 4
    REFS = 5
    FORMAT = 6
    CLEAN = 7


class Gn(BuildFileGeneratorInterface):

    def __init__(self):
        super().__init__()
        self.config = Config()
        self._regist_gn_path()

    def run(self):
        self.execute_gn_cmd(CMDTYPE.GEN)

    @throw_exception
    def execute_gn_cmd(self, cmd_type: int, **kwargs):
        if cmd_type == CMDTYPE.GEN:
            return self._execute_gn_gen_cmd()
        elif cmd_type == CMDTYPE.PATH:
            return self._execute_gn_path_cmd(kwargs)
        elif cmd_type == CMDTYPE.DESC:
            return self._execute_gn_desc_cmd(kwargs)
        elif cmd_type == CMDTYPE.LS:
            return self._execute_gn_ls_cmd(kwargs)
        elif cmd_type == CMDTYPE.REFS:
            return self._execute_gn_refs_cmd(kwargs)
        elif cmd_type == CMDTYPE.FORMAT:
            return self._execute_gn_format_cmd(kwargs)
        elif cmd_type == CMDTYPE.CLEAN:
            return self._execute_gn_clean_cmd(kwargs)
        else:
            raise OHOSException(
                'You are tring to use an unsupported gn cmd type "{}"'.format(cmd_type), '3001')

    '''Description: Get gn excutable path and regist it
    @parameter: none
    @return: Status
    '''

    @throw_exception
    def _regist_gn_path(self):
        config_data = IoUtil.read_json_file(os.path.join(
            self.config.root_path, 'build/prebuilts_download_config.json'))
        copy_config_list = config_data[os.uname().sysname.lower(
        )][os.uname().machine.lower()]['copy_config']

        gn_path = ''
        for config in copy_config_list:
            if config['unzip_filename'] == 'gn':
                gn_path = os.path.join(
                    self.config.root_path, config['unzip_dir'], 'gn')
                break

        if os.path.exists(gn_path):
            self.exec = gn_path
        else:
            raise OHOSException(
                'There is no gn executable file at {}'.format(gn_path), '0001')

    '''Description: Convert all registed args into a list
    @parameter: none
    @return: list of all registed args
    '''

    def _convert_args(self) -> list:
        args_list = []

        for key, value in self.args_dict.items():
            if isinstance(value, bool):
                args_list.append('{}={}'.format(key, str(value)).lower())

            elif isinstance(value, str):
                args_list.append('{}="{}"'.format(key, value))

            elif isinstance(value, int):
                args_list.append('{}={}'.format(key, value))

        return args_list

    '''Description: Convert all registed flags into a list
    @parameter: none
    @return: list of all registed flags
    '''

    def _covert_flags(self) -> list:
        flags_list = []

        for key, value in self.flags_dict.items():
            if value == '':
                flags_list.append('{}'.format(key))
            else:
                flags_list.append('{}={}'.format(key, str(value)).lower())

        return flags_list

    '''Description: Execute 'gn gen' command using registed args
    @parameter: kwargs TBD
    @return: None
    '''

    @throw_exception
    def _execute_gn_gen_cmd(self, **kwargs):
        gn_gen_cmd = [self.exec, 'gen',
                      '--args={}'.format(' '.join(self._convert_args())),
                      self.config.out_path] + self._covert_flags()
        if self.config.os_level == 'mini' or self.config.os_level == 'small':
            gn_gen_cmd.append(f'--script-executable={sys.executable}')
        try:
            LogUtil.write_log(self.config.log_path, 'Excuting gn command: {} {} --args="{}" {}'.format(
                self.exec, 'gen', ' '.join(self._convert_args()).replace('"', "\\\""), ' '.join(gn_gen_cmd[3:])), 'info')
            SystemUtil.exec_command(gn_gen_cmd, self.config.log_path)
        except OHOSException:
            # TODO: Analysis falied log to classify failure reason
            raise OHOSException('GN phase failed', '3000')

    def _execute_gn_path_cmd(self, **kwargs):
        pass

    def _execute_gn_desc_cmd(self, **kwargs):
        pass

    def _execute_gn_ls_cmd(self, **kwargs):
        pass

    def _execute_gn_refs_cmd(self, **kwargs):
        pass

    def _execute_gn_format_cmd(self, **kwargs):
        pass

    def _execute_gn_clean_cmd(self, **kwargs):
        pass
