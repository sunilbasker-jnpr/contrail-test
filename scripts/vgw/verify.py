from time import sleep
import fixtures
import testtools
import os
from connections import ContrailConnections
from contrail_test_init import *
from vn_test import *
from vm_test import *
from quantum_test import *
from vnc_api_test import *
from nova_test import *
from floating_ip import *
from testresources import OptimisingTestSuite, TestResource

class VerifyVgwCases():

    def test_vgw_with_fip(self, compute_type):

        fip_pool_name = 'some-pool1'
        result=True
  
        # Verification of VN
        assert self.res.vn_fixture_private.verify_on_setup()
        assert self.res.vn_fixture_dict[0].verify_on_setup()

        # Selection of compute to launch VM and VGW to configure
        host_list=[]
        vgw_compute=None
        vm_compute=None
        for host in self.inputs.compute_ips: host_list.append(self.inputs.host_data[host]['ip'])
        if len(host_list) > 1:
            for key in self.res.vgw_vn_list:
                if key.split(":")[3] == self.res.vn_fixture_dict[0].vn_name: vgw_compute = self.res.vgw_vn_list[key]['host'].split("@")[1]

            if compute_type == 'same': 
                vm_compute= self.inputs.host_data[vgw_compute]['name']
            else:
                host_list.remove(vgw_compute)
                vm_compute= self.inputs.host_data[host_list[0]]['name']
        else:
            vm_compute= self.inputs.host_data[host_list[0]]['name']
            vgw_compute=host_list[0]
         

        vm_name1= 'VGW_VM1-FIP-' + vm_compute
        # Creation of VM and validation
        vm1_fixture= self.useFixture(VMFixture(project_name= self.inputs.project_name, connections= self.connections, vn_obj= self.res.vn_fixture_private.obj, vm_name= vm_name1, node_name= vm_compute))
        assert vm1_fixture.verify_on_setup()

        # FIP Pool creation and validation 
        fip_fixture= self.useFixture(FloatingIPFixture( project_name= self.inputs.project_name, inputs = self.inputs, connections= self.connections, pool_name = fip_pool_name, vn_id= self.res.vn_fixture_dict[0].vn_id ))
        assert fip_fixture.verify_on_setup()

        # FIP pool association and validation 
        fip_id= fip_fixture.create_and_assoc_fip( self.res.vn_fixture_dict[0].vn_id, vm1_fixture.vm_id)
        assert fip_fixture.verify_fip( fip_id, vm1_fixture, self.res.vn_fixture_dict[0] )
        self.addCleanup( fip_fixture.disassoc_and_delete_fip, fip_id)

        self.logger.info( "Now trying to ping www-int.juniper.net")
        if not vm1_fixture.ping_with_certainty( 'www-int.juniper.net' ):
            result = result and False

        if not result:
            self.logger.error('Test  ping outside VN cluster from VM %s failed' %(vm1_name))
            assert result

        return True
    # End test_vgw_with_fip
   

    def test_vgw_with_native_vm(self, compute_type):

        result=True

        # Verification of VN
        assert self.res.vn_fixture_dict[0].verify_on_setup()

        # Selection of compute to launch VM and VGW to configure
        host_list=[]
        vgw_compute=None
        vm_compute=None 
        for host in self.inputs.compute_ips: host_list.append(self.inputs.host_data[host]['ip'])
        if len(host_list) > 1:
            for key in self.res.vgw_vn_list:
                if key.split(":")[3] == self.res.vn_fixture_dict[0].vn_name: vgw_compute = self.res.vgw_vn_list[key]['host'].split("@")[1]

            if compute_type == 'same':
                vm_compute= self.inputs.host_data[vgw_compute]['name']
            else:
                host_list.remove(vgw_compute)
                vm_compute= self.inputs.host_data[host_list[0]]['name']
        else:
            vm_compute= self.inputs.host_data[host_list[0]]['name']
            vgw_compute=host_list[0]

        vm_name1= 'VGW_VM1-Native-' + vm_compute
        # Creation of VM and validation
        vm1_fixture= self.useFixture(VMFixture(project_name= self.inputs.project_name, connections= self.connections, vn_obj= self.res.vn_fixture_dict[0].obj, vm_name= vm_name1, node_name= vm_compute))
        assert vm1_fixture.verify_on_setup()

        self.logger.info( "Now trying to ping www-int.juniper.net")
        if not vm1_fixture.ping_with_certainty( 'www-int.juniper.net' ):
            result = result and False

        if not result:
            self.logger.error('Test  ping outside VN cluster from VM %s failed' %(vm1_name))
            assert result

        return True
    # End test_vgw_with_native_vm

