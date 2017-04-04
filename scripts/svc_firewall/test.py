import copy
import test_v1
from tcutils.wrappers import preposttest_wrapper
from common import resource_handler
from svc_tmpl import tmpl as svc_tmpl

class Tests(test_v1.BaseTestCase_v1):

   @classmethod
   def setUpClass (cls):
       super(Tests, cls).setUpClass()

   @classmethod
   def tearDownClass (cls):
       super(Tests, cls).tearDownClass()

   def one_si_two_svm (self, param):
       tmpl = copy.deepcopy(svc_tmpl)
       objs = resource_handler.create(self, tmpl, param)
       import pdb; pdb.set_trace()
       tmpl['resources']['policy']['properties']['network_policy_entries']\
           ['network_policy_entries_policy_rule'][0]['network_policy_entries_policy_rule_action_list']\
           ['network_policy_entries_policy_rule_action_list_apply_service'] = \
             [{'list_join': [':', {'get_attr': ['svcinst', 'fq_name']}]}]
       import pdb; pdb.set_trace()
       objs = resource_handler.update(self, objs, tmpl, param)
       resource_handler.verify_on_setup(objs)
       return True

class TestwithHeat (Tests):

   @classmethod
   def setUpClass(cls):
       super(TestwithHeat, cls).setUpClass()
       cls.testmode = 'heat'

   @preposttest_wrapper
   def test_1_si_2_svm_innetnat_fw (self):
       param = {
           'parameters': {
               'mgmtvn_name': 'mgmt',
               'mgmtvn_subnet1_prefix': '1.1.1.0',
               'mgmtvn_subnet1_prefixlen': 24,
               'leftvn_name': 'left',
               'leftvn_subnet1_prefix': '1000::',
               'leftvn_subnet1_prefixlen': 64,
               'leftvn_subnet2_prefix': '100.100.100.0',
               'leftvn_subnet2_prefixlen': 24,
               'rightvn_name': 'right',
               'rightvn_subnet1_prefix': '1001::',
               'rightvn_subnet1_prefixlen': 64,
               'rightvn_subnet2_prefix': '101.101.101.0',
               'rightvn_subnet2_prefixlen': 24,
               'policy_name': 'pol', 'proto': 'any', 'action': 'pass', 'dir': '<>',
               'src_port_end': -1, 'src_port_start': -1,
               'dst_port_end': -1, 'dst_port_start': -1,
               'domain': 'default-domain', 'secgrp': ':'.join(self.inputs.project_fq_name) + ':default',
               'svctmpl_name': 'svc', 'svcinst_name': 'svc',
               'svc_type': 'firewall', 'svc_mode': 'in-network-nat', 'ha_mode': 'active-standby',
               'svc_image': 'tiny_nat_fw', 'svc_flavor': 'm1.medium',
               'svm1_name': 'svm1', 'svm2_name': 'svm2',
               'flavor': 'm1.medium', 'image': 'ubuntu-traffic',
               'leftvm_name': 'left', 'rightvm_name': 'right',
           }
       }
       return self.one_si_two_svm(param)

class TestwithVnc (TestwithHeat):

   @classmethod
   def setUpClass(cls):
       super(TestwithVnc, cls).setUpClass()
       cls.testmode = 'vnc'
