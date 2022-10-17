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

from modules.interface.setModuleInterface import SetModuleInterface
from resolver.interface.argsResolver import ArgsResolver
from services.interface.menuInterface import MenuInterface
from exceptions.ohosException import OHOSException


class OHOSSetModule(SetModuleInterface):

    _instance = None

    def __init__(self, args_dict: dict, argsResolver: ArgsResolver, menu: MenuInterface):
        super().__init__(args_dict, argsResolver, menu)
        OHOSSetModule._instance = self

    @staticmethod
    def get_instance():
        if OHOSSetModule._instance is not None:
            return OHOSSetModule._instance
        else:
            raise OHOSException(
                'OHOSSetModule has not been instantiated', '0000')

    def set_product(self):
        self.argsResolver.resolveArg(self.args_dict['product_name'], self)

    def set_parameter(self):
        self.argsResolver.resolveArg(self.args_dict['all'], self)
