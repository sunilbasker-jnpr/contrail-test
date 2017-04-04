tmpl = {
   'heat_template_version': '2015-10-15',
   'outputs': {
       'mgmtvn_id': {'value': {'get_attr': ['mgmtvn', 'fq_name']}},
       'leftvn_id': {'value': {'get_attr': ['leftvn', 'fq_name']}},
       'rightvn_id': {'value': {'get_attr': ['rightvn', 'fq_name']}},
       'policy_id': {'value': {'get_attr': ['policy', 'fq_name']}},
       'leftvm_id': {'value': {'get_resource': 'leftvm'}},
       'rightvm_id': {'value': {'get_resource': 'rightvm'}},
       'svctmpl_id': {'value': {'get_attr': ['svctmpl', 'fq_name']}},
       'svcinst_id': {'value': {'get_attr': ['svcinst', 'fq_name']}},
       'pt1_id': {'value': {'get_attr': ['pt1', 'fq_name']}},
       'pt2_id': {'value': {'get_attr': ['pt2', 'fq_name']}},
       'svm1_mgmt_id': {'value': {'get_attr': ['svm1_mgmt', 'fq_name']}},
       'svm1_left_id': {'value': {'get_attr': ['svm1_left', 'fq_name']}},
       'svm1_right_id': {'value': {'get_attr': ['svm1_right', 'fq_name']}},
       'svm2_mgmt_id': {'value': {'get_attr': ['svm2_mgmt', 'fq_name']}},
       'svm2_left_id': {'value': {'get_attr': ['svm2_left', 'fq_name']}},
       'svm2_right_id': {'value': {'get_attr': ['svm2_right', 'fq_name']}},
   },
   'parameters': {
       'domain': {'type': 'string'},
       'secgrp': {'type': 'string'},
       'mgmtvn_name': {'type': 'string'},
       'mgmtvn_subnet1_prefix': {'type': 'string'},
       'mgmtvn_subnet1_prefixlen': {'type': 'number'},
       'leftvn_name': {'type': 'string'},
       'leftvn_subnet1_prefix': {'type': 'string'},
       'leftvn_subnet1_prefixlen': {'type': 'number'},
       'leftvn_subnet2_prefix': {'type': 'string'},
       'leftvn_subnet2_prefixlen': {'type': 'number'},
       'rightvn_name': {'type': 'string'},
       'rightvn_subnet1_prefix': {'type': 'string'},
       'rightvn_subnet1_prefixlen': {'type': 'number'},
       'rightvn_subnet2_prefix': {'type': 'string'},
       'rightvn_subnet2_prefixlen': {'type': 'number'},
       'policy_name': {'type' : 'string'},
       'proto': {'type' : 'string'},
       'dir': {'type' : 'string'},
       'action': {'type' : 'string'},
       'src_port_end': {'type': 'number'},
       'src_port_start': {'type': 'number'},
       'dst_port_end': {'type': 'number'},
       'dst_port_start': {'type': 'number'},
       'svctmpl_name': {'type': 'string'},
       'svcinst_name': {'type': 'string'},
       'svc_type': {'type': 'string'},
       'svc_mode': {'type': 'string'},
       'svc_image': {'type': 'string'},
       'svc_flavor': {'type': 'string'},
       'ha_mode': {'type': 'string'},
       'svm1_name': {'type': 'string'},
       'svm2_name': {'type': 'string'},
       'leftvm_name': {'type': 'string'},
       'rightvm_name': {'type': 'string'},
       'image': {'type': 'string'},
       'flavor': {'type': 'string'},
   },
   'resources': {
       'mgmtvn': {
           'type': 'OS::ContrailV2::VirtualNetwork',
           'properties':{
               'name': {'get_param': 'mgmtvn_name'},
               'network_ipam_refs': ['default-domain:default-project:default-network-ipam'],
               'network_ipam_refs_data': [{
                   'network_ipam_refs_data_ipam_subnets': [{
                     'network_ipam_refs_data_ipam_subnets_subnet': {
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                         'get_param': 'mgmtvn_subnet1_prefix',
                       },
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                         'get_param': 'mgmtvn_subnet1_prefixlen',
                       },
                     },
                     'network_ipam_refs_data_ipam_subnets_addr_from_start' : True
                   }]
               }],
           }
       },
       'leftvn': {
           'type': 'OS::ContrailV2::VirtualNetwork',
           'depends_on': ['policy'],
           'properties':{
                 'name': {'get_param': 'leftvn_name'},
                 'network_ipam_refs': ['default-domain:default-project:default-network-ipam'],
                 'network_ipam_refs_data': [{
                   'network_ipam_refs_data_ipam_subnets': [{
                     'network_ipam_refs_data_ipam_subnets_subnet': {
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                         'get_param': 'leftvn_subnet1_prefix',
                       },
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                         'get_param': 'leftvn_subnet1_prefixlen',
                       },
                     },
                     'network_ipam_refs_data_ipam_subnets_addr_from_start' : True
                   },{
                     'network_ipam_refs_data_ipam_subnets_subnet': {
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                         'get_param': 'leftvn_subnet2_prefix',
                       },
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                         'get_param': 'leftvn_subnet2_prefixlen',
                       },
                     },
                     'network_ipam_refs_data_ipam_subnets_addr_from_start' : True
                   }]
                 }],
                 'network_policy_refs': [{'list_join': [':', {'get_attr': ['policy', 'fq_name']}]},],
                 'network_policy_refs_data': [{
                   'network_policy_refs_data_sequence': {
                     'network_policy_refs_data_sequence_major': 0,
                     'network_policy_refs_data_sequence_minor': 0
                   },
                 }],
           }
       },
       'rightvn': {
           'type': 'OS::ContrailV2::VirtualNetwork',
           'depends_on': ['policy'],
           'properties':{
                 'name': {'get_param': 'rightvn_name'},
                 'network_ipam_refs': ['default-domain:default-project:default-network-ipam'],
                 'network_ipam_refs_data': [{
                   'network_ipam_refs_data_ipam_subnets': [{
                     'network_ipam_refs_data_ipam_subnets_subnet': {
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                         'get_param': 'rightvn_subnet1_prefix',
                       },
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                         'get_param': 'rightvn_subnet1_prefixlen',
                       },
                     },
                     'network_ipam_refs_data_ipam_subnets_addr_from_start' : True
                   },{
                     'network_ipam_refs_data_ipam_subnets_subnet': {
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix': {
                         'get_param': 'rightvn_subnet2_prefix',
                       },
                       'network_ipam_refs_data_ipam_subnets_subnet_ip_prefix_len': {
                         'get_param': 'rightvn_subnet2_prefixlen',
                       },
                     },
                     'network_ipam_refs_data_ipam_subnets_addr_from_start' : True
                   }]
                 }],
                 'network_policy_refs': [{'list_join': [':', {'get_attr': ['policy', 'fq_name']}]},],
                 'network_policy_refs_data': [{
                   'network_policy_refs_data_sequence': {
                     'network_policy_refs_data_sequence_major': 0,
                     'network_policy_refs_data_sequence_minor': 0
                   },
                 }],
           }
       },
       'policy': {
           'type': 'OS::ContrailV2::NetworkPolicy',
           'properties': {
                 'name': {'get_param': 'policy_name'},
                 'network_policy_entries': {
                   'network_policy_entries_policy_rule': [{
                     'network_policy_entries_policy_rule_protocol': {'get_param': 'proto'},
                     'network_policy_entries_policy_rule_src_ports': [{
                       'network_policy_entries_policy_rule_src_ports_end_port': {'get_param': 'src_port_end'},
                       'network_policy_entries_policy_rule_src_ports_start_port': {'get_param': 'src_port_start'}
                     }],
                     'network_policy_entries_policy_rule_src_addresses': [{
                        'network_policy_entries_policy_rule_src_addresses_virtual_network': {
                           'list_join': [ ':', {'get_attr': ['leftvn', 'fq_name']}]
                        }
                     }],
                     'network_policy_entries_policy_rule_direction': {'get_param': 'dir'},
                     'network_policy_entries_policy_rule_dst_ports': [{
                       'network_policy_entries_policy_rule_dst_ports_end_port': {'get_param': 'dst_port_end'},
                       'network_policy_entries_policy_rule_dst_ports_start_port': {'get_param': 'dst_port_start'}
                     }],
                     'network_policy_entries_policy_rule_action_list': {
                       'network_policy_entries_policy_rule_action_list_simple_action': {'get_param': 'action'}
                     },
                     'network_policy_entries_policy_rule_dst_addresses': [{
                       'network_policy_entries_policy_rule_dst_addresses_virtual_network': {
                         'list_join': [':', {'get_attr': ['rightvn', 'fq_name']}]
                       }
                     }]
                   }],
                 },
           }
       },
       'svctmpl': {
           'type': 'OS::ContrailV2::ServiceTemplate',
           'properties': {
                 'domain': {'get_param': 'domain'},
                 'name': {'get_param': 'svctmpl_name'},
                 'service_template_properties': {
                   'service_template_properties_interface_type': [
                     {'service_template_properties_interface_type_service_interface_type': 'management'},
                     {'service_template_properties_interface_type_service_interface_type': 'left'},
                     {'service_template_properties_interface_type_service_interface_type': 'right'}
                   ],
                  'service_template_properties_version': 2,
                  'service_template_properties_service_type': {'get_param': 'svc_type'},
                  'service_template_properties_service_mode': {'get_param': 'svc_mode'},
                  'service_template_properties_ordered_interfaces': True
                 }
           }
       },
       'svcinst': {
           'type': 'OS::ContrailV2::ServiceInstance',
           'depends_on': ['svctmpl', 'leftvn', 'rightvn', 'mgmtvn'],
           'properties': {
                 'name': {'get_param': 'svcinst_name'},
                 'service_template_refs': [{'get_resource': 'svctmpl'}],
                 'service_instance_properties': {
                   'service_instance_properties_ha_mode': {'get_param': 'ha_mode'},
                   'service_instance_properties_interface_list': [
                     {'service_instance_properties_interface_list_virtual_network':
                       {'list_join': [':', {'get_attr': ['mgmtvn', 'fq_name']}]}
                     },
                     {'service_instance_properties_interface_list_virtual_network':
                       {'list_join': [':', {'get_attr': ['leftvn', 'fq_name']}]}
                     },
                     {'service_instance_properties_interface_list_virtual_network':
                       {'list_join': [':', {'get_attr': ['rightvn', 'fq_name']}]}
                     }
                   ]
                 },
           }
       },
       'pt1': {
           'type': 'OS::ContrailV2::PortTuple',
           'depends_on': ['svcinst'],
           'properties': {
                 'service_instance': {
                   'list_join': [':', {'get_attr': ['svcinst', 'fq_name']}]
                 }
           }
       },
       'pt2': {
           'type': 'OS::ContrailV2::PortTuple',
           'depends_on': ['svcinst'],
           'properties': {
                 'service_instance': {
                   'list_join': [':', {'get_attr': ['svcinst', 'fq_name']}]
                 }
           }
       },
       'svm1_mgmt': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['pt1'],
           'properties': {
                 'virtual_machine_interface_properties': {
                   'virtual_machine_interface_properties_service_interface_type': 'management'
                 },
                 'port_tuple_refs': [{'get_resource': 'pt1'}],
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['mgmtvn', 'fq_name']}]
                 }]
           }
       },
       'svm1_left': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['pt1'],
           'properties': {
                 'virtual_machine_interface_properties': {
                   'virtual_machine_interface_properties_service_interface_type': 'left'
                 },
                 'port_tuple_refs': [{'get_resource': 'pt1'}],
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['leftvn', 'fq_name']}]
                 }]
           }
       },
       'svm1_right': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['pt1'],
           'properties': {
                 'virtual_machine_interface_properties': {
                   'virtual_machine_interface_properties_service_interface_type': 'right'
                 },
                 'port_tuple_refs': [{'get_resource': 'pt1'}],
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['rightvn', 'fq_name']}]
                 }]
           }
       },
       'svm2_mgmt': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['pt2'],
           'properties': {
                 'virtual_machine_interface_properties': {
                   'virtual_machine_interface_properties_service_interface_type': 'management'
                 },
                 'port_tuple_refs': [{'get_resource': 'pt2'}],
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['mgmtvn', 'fq_name']}]
                 }]
           }
       },
       'svm2_left': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['pt2'],
           'properties': {
                 'virtual_machine_interface_properties': {
                   'virtual_machine_interface_properties_service_interface_type': 'left'
                 },
                 'port_tuple_refs': [{'get_resource': 'pt2'}],
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['leftvn', 'fq_name']}]
                 }]
           }
       },
       'svm2_right': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['pt2'],
           'properties': {
                 'virtual_machine_interface_properties': {
                   'virtual_machine_interface_properties_service_interface_type': 'right'
                 },
                 'port_tuple_refs': [{'get_resource': 'pt2'}],
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['rightvn', 'fq_name']}]
                 }]
           }
       },
       'svm1_mgmt_ip': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm1_mgmt' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm1_mgmt'}],
                 'virtual_network_refs': [{ 'get_resource': 'mgmtvn' }],
                 'instance_ip_family' : 'v4',
                 #'service_instance_ip' : True,
           }
       },
       'svm1_left_ip1': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm1_left' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm1_left'}],
                 'virtual_network_refs': [{ 'get_resource': 'leftvn' }],
                 'instance_ip_family' : 'v6',
                 #'service_instance_ip' : True,
           }
       },
       'svm1_left_ip2': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm1_left' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm1_left'}],
                 'virtual_network_refs': [{ 'get_resource': 'leftvn' }],
                 'instance_ip_family' : 'v4',
                 #'service_instance_ip' : True,
           }
       },
       'svm1_right_ip1': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm1_right' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm1_right'}],
                 'virtual_network_refs': [{ 'get_resource': 'rightvn' }],
                 'instance_ip_family' : 'v6',
                 #'service_instance_ip' : True,
           }
       },
       'svm1_right_ip2': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm1_right' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm1_right'}],
                 'virtual_network_refs': [{ 'get_resource': 'rightvn' }],
                 'instance_ip_family' : 'v4',
                 #'service_instance_ip' : True,
           }
       },
       'svm2_mgmt_ip': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm2_mgmt' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm2_mgmt'}],
                 'virtual_network_refs': [{ 'get_resource': 'mgmtvn' }],
                 'instance_ip_family' : 'v4',
                 #'service_instance_ip' : True,
           }
       },
       'svm2_left_ip1': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm2_left' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm2_left'}],
                 'virtual_network_refs': [{ 'get_resource': 'leftvn' }],
                 'instance_ip_family' : 'v6',
                 #'service_instance_ip' : True,
           }
       },
       'svm2_left_ip2': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm2_left' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm2_left'}],
                 'virtual_network_refs': [{ 'get_resource': 'leftvn' }],
                 'instance_ip_family' : 'v4',
                 #'service_instance_ip' : True,
           }
       },
       'svm2_right_ip1': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm2_right' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm2_right'}],
                 'virtual_network_refs': [{ 'get_resource': 'rightvn' }],
                 'instance_ip_family' : 'v6',
                 #'service_instance_ip' : True,
           }
       },
       'svm2_right_ip2': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'svm2_right' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'svm2_right'}],
                 'virtual_network_refs': [{ 'get_resource': 'rightvn' }],
                 'instance_ip_family' : 'v4',
                 #'service_instance_ip' : True,
           }
       },
       'svm1': {
           'type': 'OS::Nova::Server',
           'depends_on': [ 'svm1_left_ip1', 'svm1_left_ip2',
                           'svm1_right_ip1', 'svm1_right_ip2', 'svm1_mgmt_ip'],
           'properties': {
                 'name': { 'get_param': 'svm1_name' },
                 'image': { 'get_param':  'svc_image' },
                 'flavor': { 'get_param': 'svc_flavor' },
                 'networks': [
                   {'port': { 'get_resource': 'svm1_mgmt' }},
	           {'port': { 'get_resource': 'svm1_left' }},
                   {'port': { 'get_resource': 'svm1_right' }},
                 ]
           }
       },
       'svm2': {
           'type': 'OS::Nova::Server',
           'depends_on': [ 'svm2_left_ip1', 'svm2_left_ip2',
                           'svm2_right_ip1', 'svm2_right_ip2', 'svm2_mgmt_ip'],
           'properties': {
                 'name': { 'get_param': 'svm2_name' },
                 'image': { 'get_param':  'svc_image' },
                 'flavor': { 'get_param': 'svc_flavor' },
                 'networks': [
                   {'port': { 'get_resource': 'svm2_mgmt' }},
	           {'port': { 'get_resource': 'svm2_left' }},
                   {'port': { 'get_resource': 'svm2_right' }},
                 ]
           }
       },
       'leftvm': {
           'type': 'OS::Nova::Server',
           'depends_on': ['leftvm_port', 'leftvm_ip1', 'leftvm_ip2'],
           'properties': {
                 'flavor': {'get_param': 'flavor'},
                 'image': {'get_param': 'image'},
                 'name': {'get_param': 'leftvm_name'},
                 'networks': [{'port': {'get_resource': 'leftvm_port'}}],
           },
       },
       #'leftvm_port': {
       #  'type': 'OS::Neutron::Port',
       #  'depends_on': ['leftvn'],
       #  'properties': {'network_id': {'get_resource': 'leftvn'}},
       #},
       'leftvm_port': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['leftvn'],
           'properties': {
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['leftvn', 'fq_name']}]
                 }]
           }
       },
       'leftvm_ip1': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'leftvm_port' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'leftvm_port'}],
                 'virtual_network_refs': [{ 'get_resource': 'leftvn' }],
                 'instance_ip_family' : 'v6',
           }
       },
       'leftvm_ip2': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'leftvm_port' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'leftvm_port'}],
                 'virtual_network_refs': [{ 'get_resource': 'leftvn' }],
                 'instance_ip_family' : 'v4',
           }
       },
       'rightvm': {
           'type': 'OS::Nova::Server',
           'depends_on': ['rightvm_port', 'rightvm_ip1', 'rightvm_ip2'],
           'properties': {
                 'flavor': {'get_param': 'flavor'},
                 'image': {'get_param': 'image'},
                 'name': {'get_param': 'rightvm_name'},
                 'networks': [{'port': {'get_resource': 'rightvm_port'}}],
                 #'networks': [{'network': {'get_resource': 'rightvn'}}],
           },
       },
       #'rightvm_port': {
       #  'type': 'OS::Neutron::Port',
       #  'depends_on': ['rightvn'],
       #  'properties': {'network_id': {'get_resource': 'rightvn'}},
       #},
       'rightvm_port': {
           'type': 'OS::ContrailV2::VirtualMachineInterface',
           'depends_on': ['rightvn'],
           'properties': {
                 'security_group_refs': [{'get_param': 'secgrp'}],
                 'virtual_network_refs': [{
                   'list_join': [':', {'get_attr': ['rightvn', 'fq_name']}]
                 }]
           }
       },
       'rightvm_ip1': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'rightvm_port' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'rightvm_port'}],
                 'virtual_network_refs': [{ 'get_resource': 'rightvn' }],
                 'instance_ip_family' : 'v6',
           }
       },
       'rightvm_ip2': {
           'type': 'OS::ContrailV2::InstanceIp',
           'depends_on': [ 'rightvm_port' ],
           'properties': {
                 'virtual_machine_interface_refs': [{ 'get_resource': 'rightvm_port'}],
                 'virtual_network_refs': [{ 'get_resource': 'rightvn' }],
                 'instance_ip_family' : 'v4',
           }
       },
   }
}
