# go get github.com/wybczu/tfjson
# pylint: disable=missing-docstring, E0213, W0201
import json
import os
import sys
import shutil
import subprocess
import tempfile
import glob
from tf_assertion_helper import finder

class Runner(object):
    """Terraform converter, converting .tf files into JSON and Python.

    Pass in .tf file as argument on initialisation.
    """

    def __init__(self, snippet):
        self.snippet = snippet
        self.run()

    def _mktmpdir(self):
        """Assign make temp directory to self variable."""
        self.tmpdir = tempfile.mkdtemp()

    def _write_test_tf(self):
        """Write .tf file in temp directory."""
        tmp_mytf_file = open("%s/mytf.tf" % (self.tmpdir), "w")
        tmp_mytf_file.write(self.snippet)
        tmp_mytf_file.close()

    def _copy_tf_files(self):
        """Remove terraform cache.

        Copy all .tf files from script directory to temp directory."""
        os.system("rm -rf .terraform/modules")
        os.system("mkdir %s/mymodule" % self.tmpdir)

        files = glob.iglob(os.path.join(sys.path[0], "*.tf"))
        for file in files:
            if os.path.isfile(file):
                shutil.copy(file, "%s/mymodule" % (self.tmpdir))

    def _terraform_init(self):
        """Execute terraform init in temp directory."""
        os.system("terraform init %s" % (self.tmpdir))

    def _terraform_plan(self):
        """Execute terraform plan and save output in temp directory tfplan file."""
        os.system("terraform plan -input=false -out=%s/mytf.tfplan %s" % (self.tmpdir, self.tmpdir))

    def snippet_to_json(self):
        """Return terraform plan file as json."""
        return subprocess.check_output(["tfjson", "%s/mytf.tfplan" % (self.tmpdir)])

    @staticmethod
    def json_to_dict(json_file):
        return json.loads(json_file)

    def _removetmpdir(self):
        shutil.rmtree(self.tmpdir)

    def finder(parent, starts_with, matching_object):
        return finder(parent, starts_with, matching_object)

    def run(self):
        self._mktmpdir()
        self._write_test_tf()
        self._copy_tf_files()
        self._terraform_init()
        self._terraform_plan()
        json_snippet = self.snippet_to_json()
        result = self.json_to_dict(json_snippet)
        self.result = result
        self._removetmpdir()