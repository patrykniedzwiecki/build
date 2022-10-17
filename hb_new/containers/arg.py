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

import os
import argparse
import sys
from enum import Enum

from resources.global_var import CURRENT_BUILD_ARGS
from resources.global_var import DEFAULT_BUILD_ARGS

from resources.global_var import CURRENT_SET_ARGS
from resources.global_var import DEFAULT_SET_ARGS

from resources.global_var import CURRENT_CLEAN_ARGS
from resources.global_var import DEFAULT_CLEAN_ARGS

from resources.global_var import DEFAULT_ENV_ARGS
from resources.global_var import CURRENT_ENV_ARGS

from resources.global_var import ARGS_DIR

from exceptions.ohosException import OHOSException
from util.logUtil import LogUtil
from util.ioUtil import IoUtil
from util.typeCheckUtil import TypeCheckUtil
from resolver.argsFactory import ArgsFactory
from containers.status import throw_exception


class ModuleType(Enum):
    BUILD = 0
    SET = 1
    ENV = 2
    CLEAN = 3
    TOOL = 4
    HELP = 5


class ArgType():

    NONE = 0
    BOOL = 1
    INT = 2
    STR = 3
    LIST = 4
    DICT = 5
    GATE = 6

    @staticmethod
    def getType(value: str):
        if value == 'bool':
            return ArgType.BOOL
        elif value == "int":
            return ArgType.INT
        elif value == 'str':
            return ArgType.STR
        elif value == "list":
            return ArgType.LIST
        elif value == 'dict':
            return ArgType.DICT
        elif value == 'gate':
            return ArgType.GATE
        else:
            return ArgType.NONE


class BuildPhase():

    NONE = 0
    PRE_BUILD = 1
    PRE_LOAD = 2
    LOAD = 3
    PRE_TARGET_GENERATE = 4
    TARGET_GENERATE = 5
    POST_TARGET_GENERATE = 6
    PRE_TARGET_COMPILATION = 7
    TARGET_COMPILATION = 8
    POST_TARGET_COMPILATION = 9
    POST_BUILD = 10

    @staticmethod
    def getType(value: str):
        if value == 'prebuild':
            return BuildPhase.PRE_BUILD
        elif value == "preload":
            return BuildPhase.PRE_LOAD
        elif value == 'load':
            return BuildPhase.LOAD
        elif value == "preTargetGenerate":
            return BuildPhase.PRE_TARGET_GENERATE
        elif value == 'targetGenerate':
            return BuildPhase.TARGET_GENERATE
        elif value == 'postTargetGenerate':
            return BuildPhase.POST_TARGET_GENERATE
        elif value == 'preTargetCompilation':
            return BuildPhase.PRE_TARGET_COMPILATION
        elif value == 'targetCompilation':
            return BuildPhase.TARGET_COMPILATION
        elif value == 'postTargetCompilation':
            return BuildPhase.POST_TARGET_COMPILATION
        elif value == 'postbuild':
            return BuildPhase.POST_BUILD
        else:
            return BuildPhase.NONE


class CleanPhase():

    REGULAR = 0
    DEEP = 1
    NONE = 2

    @staticmethod
    def getType(value: str):
        if value == 'regular':
            return CleanPhase.REGULAR
        elif value == 'deep':
            return CleanPhase.DEEP
        else:
            return CleanPhase.NONE


class Arg():

    def __init__(self, name: str, help: str, phase: str,
                 attribute: dict, argtype: ArgType, value,
                 resolveFuntion: str):
        self._argName = name
        self._argHelp = help
        self._argPhase = phase
        self._argAttribute = attribute
        self._argType = argtype
        self._argValue = value
        self._resolveFuntion = resolveFuntion

    @property
    def argName(self):
        return self._argName

    @property
    def argValue(self):
        return self._argValue

    @argValue.setter
    def argValue(self, value):
        self._argValue = value

    @property
    def argHelp(self):
        return self._argHelp

    @property
    def argAttribute(self):
        return self._argAttribute

    @property
    def argPhase(self):
        return self._argPhase

    @property
    def argType(self):
        return self._argType

    @property
    def resolveFuntion(self):
        return self._resolveFuntion

    @resolveFuntion.setter
    def resolveFuntion(self, value):
        self._resolveFuntion = value

    @staticmethod
    @throw_exception
    def createInstanceByDict(data: dict):
        arg_name = str(data['argName']).replace("-", "_")[2:]
        arg_help = str(data['argHelp'])
        arg_phase = BuildPhase.getType(str(data['argPhase']))
        arg_attibute = dict(data['argAttribute'])
        arg_type = ArgType.getType(data['argType'])
        arg_value = ''
        if arg_type == ArgType.BOOL or arg_type == ArgType.GATE:
            arg_value = data['argDefault']
        elif arg_type == ArgType.INT:
            arg_value = int(data['argDefault'])
        elif arg_type == ArgType.STR:
            arg_value = data['argDefault']
        elif arg_type == ArgType.LIST:
            arg_value = list(data['argDefault'])
        elif arg_type == ArgType.DICT:
            arg_value = dict(data['argDefault'])
        else:
            raise OHOSException('Unknown arg type "{}" for arg "{}"'.format(
                arg_type, arg_name), "0003")
        resolveFuntion = data['resolveFuntion']
        return Arg(arg_name, arg_help, arg_phase, arg_attibute, arg_type, arg_value, resolveFuntion)

    @staticmethod
    def print_help(module_type: ModuleType):
        parser = argparse.ArgumentParser()
        all_args = Arg.read_args_file(module_type)

        for arg in all_args.values():
            arg = dict(arg)
            ArgsFactory.genenic_add_option(parser, arg)

        parser.parse_known_args(sys.argv[2:])
        parser.print_help()

    @staticmethod
    def parse_all_args(module_type: ModuleType) -> dict:
        args_dict = {}
        parser = argparse.ArgumentParser()
        all_args = Arg.read_args_file(module_type)

        for arg in all_args.values():
            arg = dict(arg)
            ArgsFactory.genenic_add_option(parser, arg)
            oh_arg = Arg.createInstanceByDict(arg)
            args_dict[oh_arg.argName] = oh_arg

        parser_args = parser.parse_known_args(sys.argv[2:])

        for oh_arg in args_dict.values():
            if isinstance(oh_arg, Arg):
                assigned_value = parser_args[0].__dict__[oh_arg.argName]
                if oh_arg.argType == ArgType.LIST:
                    assigned_value = TypeCheckUtil.tile_list(assigned_value)
                    assigned_value = list(set(assigned_value))
                elif oh_arg.argType == ArgType.BOOL or oh_arg.argType == ArgType.GATE:
                    assigned_value = bool(assigned_value)

                if oh_arg.argAttribute.get('deprecated', None) and oh_arg.argValue != assigned_value:
                    LogUtil.hb_warning(
                        'compile option "{}" will be deprecated, please consider use other options'.format(oh_arg.argName))
                oh_arg.argValue = assigned_value
                Arg.write_args_file(
                    oh_arg.argName, oh_arg.argValue, module_type)

        return args_dict

    @staticmethod
    @throw_exception
    def write_args_file(key: str, value, module_type: ModuleType):
        args_file_path = ''
        if module_type == ModuleType.BUILD:
            args_file_path = CURRENT_BUILD_ARGS
        elif module_type == ModuleType.SET:
            args_file_path = CURRENT_SET_ARGS
        elif module_type == ModuleType.CLEAN:
            args_file_path = CURRENT_CLEAN_ARGS
        elif module_type == ModuleType.ENV:
            args_file_path = CURRENT_ENV_ARGS
        else:
            raise OHOSException(
                'You are trying to write args file, but there is no corresponding module "{}" args file'
                .format(module_type), "0002")
        args_file = Arg.read_args_file(module_type)
        args_file[key]["argDefault"] = value
        IoUtil.dump_json_file(args_file_path, args_file)

    @staticmethod
    @throw_exception
    def read_args_file(module_type: ModuleType):
        args_file_path = ''
        default_file_path = ''
        if module_type == ModuleType.BUILD:
            args_file_path = CURRENT_BUILD_ARGS
            default_file_path = DEFAULT_BUILD_ARGS
        elif module_type == ModuleType.SET:
            args_file_path = CURRENT_SET_ARGS
            default_file_path = DEFAULT_SET_ARGS
        elif module_type == ModuleType.CLEAN:
            args_file_path = CURRENT_CLEAN_ARGS
            default_file_path = DEFAULT_CLEAN_ARGS
        elif module_type == ModuleType.ENV:
            args_file_path = CURRENT_ENV_ARGS
            default_file_path = DEFAULT_ENV_ARGS
        else:
            raise OHOSException(
                'You are trying to write args file, but there is no corresponding module "{}" args file'
                .format(module_type), "0002")
        if not os.path.exists(args_file_path):
            IoUtil.copy_file(src=default_file_path, dst=args_file_path)
        return IoUtil.read_json_file(args_file_path)

    @staticmethod
    def clean_args_file():
        for file in os.listdir(ARGS_DIR):
            if file.endswith('.json') and os.path.exists(os.path.join(ARGS_DIR, file)):
                os.remove(os.path.join(ARGS_DIR, file))
