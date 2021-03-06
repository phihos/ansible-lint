# Copyright (c) 2020 Sorin Sbarnea <sorin.sbarnea@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from ansiblelint.rules import AnsibleLintRule


class MissingFilePermissionsRule(AnsibleLintRule):
    id = "208"
    shortdesc = 'File permissions not mentioned'
    description = (
        "Missing mode parameter can cause unexpected file permissions based "
        "on version of Ansible being used. Be explicit, or if you still "
        "want the default behavior you can use ``mode: preserve`` to avoid "
        "hitting this rule. See "
        "https://github.com/ansible/ansible/issues/71200"
    )
    severity = 'VERY_HIGH'
    tags = ['unpredictability']
    version_added = 'v4.3.0'

    _modules = (
        'assemble',
        'archive',
        'copy',
        'file',
        'replace',
        'template',
        'unarchive',
    )

    _modules_with_create = (
        'blockinfile',
        'ini_file',
        'lineinfile'
    )

    def matchtask(self, file, task):
        if task["action"]["__ansible_module__"] not in self._modules and \
                task["action"]["__ansible_module__"] not in self._modules_with_create:
            return False

        if task["action"]["__ansible_module__"] in self._modules_with_create and \
                not task["action"].get("create", False):
            return False

        # A file that doesn't exist cannot have a mode
        if task['action'].get('state', None) == "absent":
            return False

        # A symlink always has mode 0o777
        if task['action'].get('state', None) == "link":
            return False

        # The file module does not create anything when state==file (default)
        if task["action"]["__ansible_module__"] == "file" and \
                task['action'].get('state', 'file') == 'file':
            return False

        mode = task['action'].get('mode', None)
        return mode is None
