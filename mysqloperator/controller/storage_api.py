# Copyright (c) 2020, Oracle and/or its affiliates.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2.0,
# as published by the Free Software Foundation.
#
# This program is also distributed with certain software (including
# but not limited to OpenSSL) that is licensed under separate terms, as
# designated in a particular file or component or in included license
# documentation.  The authors of MySQL hereby grant you an additional
# permission to link the program and your derivative works with the
# separately licensed software that they have included with MySQL.
# This program is distributed in the hope that it will be useful,  but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License, version 2.0, for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

from .api_utils import dget_dict, dget_str, dget_int, dget_bool, dget_list, ApiSpecError
from .utils import merge_patch_object, indent
import yaml

class CustomStorageSpec:
    helperImage = None
    beforeScript = None
    afterScript = None
    secretsName = None
    secretsKeys = None # map: variable -> key


# TODO volume instead of persistentVolumeClaim?
class PVCStorageSpec:
    raw_data = None

    def add_to_pod_spec(self, pod_spec, container_name):
        patch = f"""
spec:
    containers:
    - name: {container_name}
      volumeMounts:
      - name: tmp-storage
        mountPath: /mnt/storage
    volumes:
    - name: tmp-storage
{indent(yaml.safe_dump(self.raw_data), 6)}
"""
        merge_patch_object(pod_spec, yaml.safe_load(patch))


    def parse(self, spec, prefix):
        self.raw_data = spec


class OCIOSStorageSpec:
    bucketName = None
    prefix = None
    apiKeySecretName = None

    def add_to_pod_spec(self, pod_spec, container_name):
        patch = f"""
spec:
    containers:
    - name: {container_name}
      volumeMounts:
      - name: secrets-volume
        readOnly: true
        mountPath: "/.oci"
    volumes:
    - name: secrets-volume
      secret:
        defaultMode: 400
        secretName: {self.apiKeySecretName}
"""
        merge_patch_object(pod_spec, yaml.safe_load(patch))


    def parse(self, spec, prefix):
        self.bucketName = dget_str(spec, "bucketName", prefix)

        self.apiKeySecretName = dget_str(spec, "apiKeySecretName", prefix)



ALL_STORAGE_SPEC_TYPES = {
    "ociObjectStorage": OCIOSStorageSpec,
    "persistentVolumeClaim" : PVCStorageSpec
}

class StorageSpec:
    ociObjectStorage = None
    persistentVolumeClaim = None

    def __init__(self, allowed_types=ALL_STORAGE_SPEC_TYPES):
        if isinstance(allowed_types, dict):
            self._allowed_types = allowed_types
        else:
            assert isinstance(allowed_types, list)

            self._allowed_types = {}
            for t in allowed_types:
                self._allowed_types[t] = ALL_STORAGE_SPEC_TYPES[t]

    def add_to_pod_spec(self, pod_spec, container_name):
        if self.ociObjectStorage:
            self.ociObjectStorage.add_to_pod_spec(pod_spec, container_name)
        if self.persistentVolumeClaim:
            self.persistentVolumeClaim.add_to_pod_spec(pod_spec, container_name)

    def parse(self, spec, prefix):
        storage_spec = None
        storage_class = None
        storage_keys = []
        for k, v in self._allowed_types.items():
            tmp = dget_dict(spec, k, prefix, {})
            if tmp:
                storage_spec = tmp
                storage_class = v
                storage_keys.append(k)

        if len(storage_keys) > 1:
            raise ApiSpecError(f"Only one of {', '.join(storage_keys)} must be set in {prefix}")
        elif len(storage_keys) == 0:
            raise ApiSpecError(f"One of {', '.join(storage_keys)} must be set in {prefix}")

        storage = storage_class()
        storage.parse(storage_spec, prefix + "." + storage_keys[0])
        setattr(self, storage_keys[0], storage)