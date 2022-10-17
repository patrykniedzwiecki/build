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

from containers.arg import Arg
from resolver.interface.argsResolverInterface import ArgsResolverInterface


class ArgsResolver():

    def __init__(self, argsResolver: ArgsResolverInterface):
        self._argsResolver = argsResolver

    def resolveArg(self, targetArg: Arg, module):
        self._argsResolver.resolveArg(targetArg, module)
