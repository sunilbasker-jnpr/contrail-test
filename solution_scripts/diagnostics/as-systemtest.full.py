import os
import threading
import argparse
import sys
import copy

import pdb
import re
from netaddr import IPNetwork
import ipaddr
from tcutils.cfgparser import parse_cfg_file
from common.contrail_test_init import ContrailTestInit
from common.connections import ContrailConnections
import  yaml
from tcutils import *
from config import *

OS_USERNAME    = os.environ['OS_USERNAME']
OS_PASSWORD    = os.environ['OS_PASSWORD']
OS_TENANT_NAME = os.environ['OS_TENANT_NAME']
OS_AUTH_URL    = os.environ['OS_AUTH_URL']

import string
import random
from common.contrail_test_init import ContrailTestInit
import multiprocessing as mp
from common import log_orig as logging
from common.connections import ContrailConnections
from send_zmq import *
from traffic import *

#debug_func()
#sys.exit()

def parse_yaml_cfg_file(conf_file):
  
   fp = open(conf_file,"r")
   conf = yaml.load(fp)

   return conf
 
class Struct(object):
    def __init__(self, entries):
        self.__dict__.update(entries)

def validate_args(args):
    for key, value in args.__dict__.iteritems():
        if value == 'None':
            args.__dict__[key] = None
        if value == 'False':
            args.__dict__[key] = False
        if value == 'True':
            args.__dict__[key] = True

def update_args(ini_args, cli_args):
    for key in cli_args.keys():
        if cli_args[key]:
            ini_args[key] = cli_args[key]
    return ini_args

def parse_cli(args):

    parser = argparse.ArgumentParser(description=__doc__)
    args, remaining_argv = parser.parse_known_args(sys.argv[1:])
    print "args:",args

def delete_mgmt_vn(conn_obj_list,thread_count,global_conf,tenant_conf):

    mgmt_vn_name   = global_conf['mgmt,vn_name']

    router_obj = RouterConfig(None)
    pr_names   = router_obj.retrieve_existing_pr(conn_obj_list=conn_obj_list)
    kwargs = {}
    kwargs['tenant_name'] = 'admin'
    kwargs['vn_name']     = [u'default-domain',u'admin',unicode(mgmt_vn_name)]
    kwargs['mx_list']     = pr_names
    pr_obj_list = []
    vn_obj = VN(None)
    for router_name in pr_names:
        pr_obj = vn_obj.retrieve_pr_obj(conn_obj_list=conn_obj_list,router_name=router_name)
        if pr_obj:
           pr_obj_list.append(pr_obj)

    vn_ids = vn_obj.get_vn_ids(conn_obj_list=conn_obj_list,tenant_name_list=['admin'],vn_names_list=[mgmt_vn_name])
     
    kwargs_list = []
    if len(pr_obj_list) != 0:
       for pr_obj in pr_obj_list:
           kwargs = {}
           kwargs['pr_obj']      = pr_obj
           kwargs['vn_list']     = vn_ids
           kwargs_list.append(kwargs)
       kwargs = {'kwargs_list': kwargs_list } if len(kwargs_list) > 1 else kwargs_list[0]
       vn_obj.delete_extend_to_pr(count=thread_count,conn_obj_list=conn_obj_list,**kwargs)

    kwarg = {}
    kwarg['tenant_name'] = 'admin'
    kwarg['vn_name']     = mgmt_vn_name
    vn_obj = VN(None)
    vn_obj.delete_vn_by_name_process(count=thread_count,conn_obj_list=[conn_obj_list[0]],**kwarg)

def create_mgmt_vn_ipam(conn_obj_list,thread_count,global_conf,tenant_conf):

    mgmt_vn_name   = global_conf['mgmt,vn_name']

    ipam_name_pattern = global_conf['ipam,name,pattern']
    ipam_name = re.sub(global_conf['test_id,replace_str'],str(global_conf['test_id']),ipam_name_pattern)
    mgmt_domain_name_pattern = global_conf['mgmt,vdns_domain_name_pattern']
    mgmt_domain_name         = re.sub(global_conf['test_id,replace_str'],str(global_conf['test_id']),mgmt_domain_name_pattern)
    mgmt_domain_name         = re.sub('\.','-',mgmt_domain_name)

    ipam_obj = IPAM(None)
    kwargs = {}
    kwargs['tenant_name'] = 'admin'
    kwargs['ipam_name']   = ipam_name
    kwargs['domain_server_name'] = mgmt_domain_name
    ipam_obj.create_ipam(count=1,conn_obj_list=conn_obj_list,**kwargs)
    mgmt_cidr      = global_conf['mgmt,cidr_start']
    mgmt_cidr_obj  = CIDR(mgmt_cidr)
    cidr           = mgmt_cidr_obj.get_next_cidr()

    conf = {}
    conf['cidr']         = cidr
    conf['ipam_name']    = ipam_name
    conf['tenant_name']  = 'admin'
    conf['vn_name']      = mgmt_vn_name
    conf['disable_gateway'] = True
    conf['shared_flag']     = True
    conf['use_fixture']     = True
    conf['external_flag']   = global_conf['mgmt,external_flag']

    vn_obj  = VN(None)
    extend_to_pr,mgmt_vn_fqname,mgmt_vn_uuid = vn_obj.create_vn(count=thread_count,conn_obj_list=conn_obj_list,**conf)
    return mgmt_vn_fqname,mgmt_vn_uuid

def get_mysql_token():

    fptr = open("/etc/contrail/mysql.token","r")
    return fptr.readline().strip()
 
class Test(object):

    def __init__(self,yaml_global_conf,ini_global_conf,test_conf):

        self.yaml_global_conf = yaml_global_conf
        self.ini_global_conf = ini_global_conf
        self.test_conf = test_conf
        self.tenant_conf = test_conf['tenants']

    def cleanup_tenant(self):
        tenant_name_list = self.global_conf['tenant_name_list']
        conn_obj_list = self.conn_obj_list
        func_arg = conn_obj_list,self.thread_count,self.global_conf,self.tenant_conf,tenant_name_list
        proj_obj = ProjectConfig(None)

        print "tenant_name_list:",tenant_name_list
        func_arg = conn_obj_list,self.thread_count,self.global_conf,self.tenant_conf,tenant_name_list

        #bgpaas_obj = Bgpaas(None)
        #bgpaas_obj.delete_bgpaas(*func_arg)

        vm_obj = VM(None)
        vm_obj.delete_vms(*func_arg)

        fip_obj = FloatingIPPool(None)
        fip_obj.delete_fip_pools(*func_arg)

        lr_obj    = LogicalRouterConfig(None)
        lr_obj.delete_logical_routers(*func_arg)

        router_obj = RouterConfig(None)
        router_obj.delete_logical_interfaces(*func_arg)

        lbaas_obj = Lbaas(None)
        lbaas_obj.delete_health_monitors(*func_arg)
        lbaas_obj.delete_lb_members(*func_arg)

        vm_obj = VM(None)
        vm_obj.delete_vms(*func_arg)
        vm_obj.delete_vmis(*func_arg)

        vn_obj = VN(None)
        vn_obj.delete_extend_to_physical_routers(*func_arg)

        lbaas_obj = Lbaas(None)
        lbaas_obj.delete_lb_vips(*func_arg)
        lbaas_obj.delete_lb_pools(*func_arg)
 
        vn_obj = VN(None)
        vn_obj.delete_vns(*func_arg)

        ipam_obj   = IPAM(None)
        ipam_obj.delete_ipams(*func_arg)

        policy_obj = Policy(None)
        #policy_obj.detach_policies(*func_arg)
        policy_obj.delete_policies(*func_arg)

        project_obj = ProjectConfig(None)
        project_obj.delete_tenants(*func_arg)

        vdns_obj = vDNS(None)
        vdns_obj.delete_record_per_tenant(*func_arg)
        time.sleep(2)
 
    def get_vm_info(self):
        
        conn_obj_list = self.conn_obj_list
        tenant_name_list = self.global_conf['tenant_name_list']
        vm_obj = VM(None)
        return vm_obj.retrieve_vm_info(conn_obj_list=conn_obj_list,tenant_name_list=tenant_name_list,global_conf=self.global_conf,tenant_conf=self.tenant_conf)

    def get_vlan_info(self):
        conn_obj_list = self.conn_obj_list
        router_obj = RouterConfig(None)
        vlan_info  = router_obj.retrieve_pr_vlan_info(conn_obj_list=conn_obj_list,global_conf=self.global_conf) 
        return vlan_info

    def cleanup_global_config(self):
        conn_obj_list = self.conn_obj_list
        func_arg = [self.thread_count,self.global_conf,self.tenant_conf]
        lls_obj = LLS(None)
        lls_obj.delete_link_local_services(conn_obj_list,*func_arg)

        routerconf_obj = RouterConfig(None)
        func_arg1 = func_arg[:]
        func_arg1.append(['admin'])
        routerconf_obj.delete_logical_interfaces(conn_obj_list,*func_arg1)
        routerconf_obj.delete_physical_interfaces(conn_obj_list,*func_arg)
        routerconf_obj.delete_physical_routers(conn_obj_list,*func_arg)

        delete_mgmt_vn(conn_obj_list,*func_arg)

        # delete mgmt IPAM
        ipam_name_pattern        = self.global_conf['ipam,name,pattern']
        ipam_name                = re.sub(self.global_conf['test_id,replace_str'],str(self.global_conf['test_id']),ipam_name_pattern)
        mgmt_domain_name_pattern = self.global_conf['mgmt,vdns_domain_name_pattern']
        mgmt_domain_name         = re.sub(self.global_conf['test_id,replace_str'],str(self.global_conf['test_id']),mgmt_domain_name_pattern)
        mgmt_domain_name         = re.sub('\.','-',mgmt_domain_name)

        args_list = [1]
        kwargs    = {'tenant_name':'admin','ipam_name':ipam_name}
        ipam_obj  = IPAM(None)
        ipam_obj.delete_ipam(count=self.thread_count,conn_obj_list=[conn_obj_list[0]],**kwargs)
        vdns_obj = vDNS(None)
        vdns_obj.delete_vdns(conn_obj_list)

        return

    def parse_cli_args(self,args):
        """
          --tenant_count use cli count else count from yaml
          --tenant_index 200:10000 or default: 0-650
          --tenant_index_random # if mentioned,index should be random,else start from initial index

          --tenant_name_prefix  # default:None ( use yaml ).If configured use to generate tenant names

          --tenant_name         # default:None.If configured,act on particular tenant name
        """   
        self.global_conf['cli,tenant_count']         = int(args.tenant_count)
        self.global_conf['cli,tenant_index_range']   = args.tenant_index_range
        self.global_conf['cli,tenant_index_random']  = args.tenant_index_random
        self.global_conf['cli,tenant_name_prefix']   = args.tenant_name_prefix
        self.global_conf['cli,tenant_name']          = args.tenant_name
        self.global_conf['cli,action,create']        = args.create
        self.global_conf['cli,action,delete']        = args.delete
        self.global_conf['cli,action,create_global'] = args.create_global
        self.global_conf['cli,action,delete_global'] = args.delete_global
        self.global_conf['tenant_index_range']  = self.global_conf['cli,tenant_index_range']
        self.global_conf['tenant_index_random'] = self.global_conf['cli,tenant_index_random']

        if self.global_conf['cli,action,create'] or self.global_conf['cli,action,create_global'] :
           create = True
        elif self.global_conf['cli,action,delete'] or self.global_conf['cli,action,delete_global']:
           create = False
        else:
           create = None

        if self.global_conf['cli,tenant_count'] != 0 :
           self.global_conf['tenant_count'] = self.global_conf['cli,tenant_count']
        else:
           self.global_conf['tenant_count'] = self.tenant_conf['tenant,count']

        tenant_name  = self.global_conf['cli,tenant_name']
        if args.tenant_name_prefix:
           tenant_name_prefix = args.tenant_name_prefix
        else:
           tenant_name_prefix = self.tenant_conf['tenant,name_prefix']
        tenant_count = self.global_conf['tenant_count']
        tenant_index = self.global_conf['tenant_index_range'].split(":") 
        tenant_index_start = int(tenant_index[0])
        if len(tenant_index) == 1:
           tenant_index_end = 650
        else:
           tenant_index_end = int(tenant_index[1])

        self.conn_obj_list = create_connections(self.thread_count)

        proj_obj = ProjectConfig(None)
        if tenant_name and string.upper(tenant_name) == "ALL":
           # for delete/traffic only
           existing_tenants = proj_obj.retrieve_configured_tenant_list(conn_obj_list=self.conn_obj_list) 
           tenant_name_list = existing_tenants[:]
        elif tenant_name and string.upper(tenant_name) == "ALL_TEST" :
           # for delete/traffic only
           existing_tenants = proj_obj.retrieve_configured_tenant_list(conn_obj_list=self.conn_obj_list) 
           for tenant in existing_tenants:
               if re.search(tenant_name_prefix,tenant):
                   tenant_name_list.append(tenant)
        elif tenant_name :
           # do action for particular tenant_name
           tenant_name_list = []
           if re.search(tenant_name_prefix,tenant_name):
              tenant_name_list.append(tenant_name)
        elif tenant_name is None:
           tenant_name_list = []
           if create:
              while len(tenant_name_list) != tenant_count:
                    if self.global_conf['tenant_index_random']:
                       index = random.randint(tenant_index_start,tenant_index_end)
                    else:
                       if len(tenant_name_list) == 0:
                          index = tenant_index_start
                    tenant_name = tenant_name_prefix + "." + str(index)
                    index += 1
                    if tenant_name in tenant_name_list:
                       continue
                    tenant_name_list.append(tenant_name)
           else: # --delete/traffic only
              existing_tenants = proj_obj.retrieve_configured_tenant_list(conn_obj_list=self.conn_obj_list)
              filtered_tenants = []
              for tenant in existing_tenants:
                  ret = re.search('(\d+)',tenant)
                  if ret and int(ret.group(1)) >= tenant_index_start and \
                              int(ret.group(1)) <= tenant_index_end:
                     filtered_tenants.append(tenant)
              if self.global_conf['tenant_index_random']:
                 for i in xrange(tenant_count):
                    random.shuffle(filtered_tenants)
                    tenant_name_list.append(filtered_tenants[0])
                    filtered_tenants.pop(0)
              else:
                 tenant_name_list = filtered_tenants[0:tenant_count] 

        return tenant_name_list

    def parse_config(self):

        self.global_conf = {}
        self.tenant_conf = {}
        self.traffic_conf = {}

        self.global_conf['glance,image_name'] = self.ini_global_conf['GLOBALS']['glance_image_name']
        self.thread_count                     = int(self.ini_global_conf['GLOBALS']['thread_count'])

        self.test_name               = self.test_conf['name']
        self.global_conf['test_id']  = self.test_conf['id']
        self.global_conf['test_id,replace_str'] = 'ZZZ'

        self.global_conf['mgmt,vn_name']                  = self.yaml_global_conf['virtual_network']['name']
        self.global_conf['mgmt,subnet_name']              = self.yaml_global_conf['virtual_network']['name'] + "_subnet"
        self.global_conf['mgmt,external_flag']            = self.yaml_global_conf['virtual_network']['adv_options']['external_flag']
        self.global_conf['mgmt,cidr_start']               = self.yaml_global_conf['virtual_network']['subnets'][0]['cidr']
        self.global_conf['mgmt,vdns_domain_name_pattern'] = self.yaml_global_conf['vDNS']['domain_name']
        self.global_conf['pr_mx']  = self.yaml_global_conf.get('pr_mx',[])
        self.global_conf['pr_qfx'] = self.yaml_global_conf.get('pr_qfx',[])

        lls_conf = self.yaml_global_conf.get('LLS',None)
        if lls_conf:
           self.global_conf['lls,name']       = lls_conf['name']
           self.global_conf['lls,count']      = lls_conf['count']
           self.global_conf['lls,start_ip']   = lls_conf['lls_ip']
           self.global_conf['lls,start_port'] = lls_conf['lls_port']
           self.global_conf['lls,fab_ip']     = lls_conf['fab_ip']
           self.global_conf['lls,fab_port']   = lls_conf['fab_port']
           self.global_conf['lls,fab_dns']    = lls_conf['fab_dns']

        global_vdns_conf = self.yaml_global_conf.get('vDNS',None)
        if global_vdns_conf:
           self.global_conf['vdns,name_pattern']         = global_vdns_conf['name']
           self.global_conf['vdns,domain_name,pattern']  = global_vdns_conf['domain_name']
           self.global_conf['vdns,dyn_updates']          = global_vdns_conf['dyn_updates']
           self.global_conf['vdns,rec_resolution_order'] = global_vdns_conf['rec_resolution_order']
           self.global_conf['vdns,floating_ip_record']   = global_vdns_conf['floating_ip_record']
           self.global_conf['vdns,ttl']                  = global_vdns_conf['ttl']
           self.global_conf['vdns,forwarder']            = global_vdns_conf['forwarder']
           self.global_conf['vdns,external_visible']     = global_vdns_conf['external_visible']
           self.global_conf['vdns,reverse_resolution']   = global_vdns_conf['reverse_resolution']

        global_ipam_conf = self.yaml_global_conf.get('IPAM',None)
        if global_ipam_conf:
           self.global_conf['ipam,name,pattern']  = global_ipam_conf['name']
           self.global_conf['ipam,count']         = global_ipam_conf['count']

        st_conf = self.yaml_global_conf.get('service_chain',None)
        if st_conf:
           st = st_conf['service_template']
           self.global_conf['service_templates'] = st

        tenant_conf              = self.test_conf['tenants'][0]
        self.tenant_conf['tenant,name_prefix']       = tenant_conf['name_prefix']
        self.tenant_conf['tenant,count']             = tenant_conf['count'] 
        self.tenant_conf['tenant,index,replace_str'] = 'XXX'
        self.tenant_conf['tenant,vn_group_list']     = []

        tenant_network_conf      = tenant_conf['virtual_networks']
        self.tenant_conf['tenant,vn_group_list'] = []
        self.tenant_conf['vn,index,replace_str'] = 'YYY'

        lbaas_conf = tenant_conf.get('Lbaas',None)
        if lbaas_conf:
           tenant_lbaas_conf = tenant_conf['Lbaas'][0]
           self.tenant_conf['lbaas,pool_name']         = tenant_lbaas_conf['pool_name']
           self.tenant_conf['lbaas,count']             = tenant_lbaas_conf['count']
           self.tenant_conf['lbaas,method']            = tenant_lbaas_conf['method']
           self.tenant_conf['lbaas,pool,protocol']     = tenant_lbaas_conf['pool_protocol']
           self.tenant_conf['lbaas,pool,members_port'] = tenant_lbaas_conf['pool_members'][0]['port']
           pool_vip_conf = tenant_lbaas_conf['pool_vip']
           self.tenant_conf['lbaas,pool,vip_name']     = pool_vip_conf['vip_name']
           self.tenant_conf['lbaas,pool,vip_port']     = pool_vip_conf['port']
           self.tenant_conf['lbaas,pool,vip_protocol'] = pool_vip_conf['protocol']
           probe_conf    = tenant_lbaas_conf['probe']
           self.tenant_conf['lbaas,probe,type']    = probe_conf['type']
           self.tenant_conf['lbaas,probe,delay']   = probe_conf['delay']
           self.tenant_conf['lbaas,probe,timeout'] = probe_conf['timeout']
           self.tenant_conf['lbaas,probe,retries'] = probe_conf['retries']
        
        for i in xrange(len(tenant_network_conf)):
            vn_info                    = {}
            vn_info['vn,name,pattern'] = tenant_network_conf[i]['name']
            vn_info['count']           = tenant_network_conf[i]['count']
            vn_info['subnet,count']    = tenant_network_conf[i]['subnets'][0]['count']
            #vn_info['subnet,cidr']     = tenant_network_conf[i]['subnets'][0]['cidr']
            vn_info['attach_fip']      = tenant_network_conf[i].get('attach_fip',None)
            vn_info['attach_policy']   = tenant_network_conf[i].get('attach_policy',None)
            vn_info['fwd_mode']        = tenant_network_conf[i].get('fwd_mode','l2_l3')
            if tenant_network_conf[i].has_key('vm'):
              vn_info['vm,name_pattern'] = tenant_network_conf[i]['vm']['name']
              vn_info['vm,count']        = tenant_network_conf[i]['vm']['count']
              glance_image = tenant_network_conf[i]['vm'].get('image',None)
              if glance_image:
                 vn_info['vm,glance_image'] = glance_image
              else:
                 vn_info['vm,glance_image'] = self.global_conf['glance,image_name']
            if tenant_network_conf[i].has_key('bgp_vm'):
              vn_info['bgp_vm,name_pattern'] = tenant_network_conf[i]['bgp_vm']['name']
              vn_info['bgp_vm,count']        = tenant_network_conf[i]['bgp_vm']['count']
              glance_image = tenant_network_conf[i]['bgp_vm'].get('image',None)
              if glance_image:
                 vn_info['bgp_vm,glance_image'] = glance_image
              else:
                 vn_info['bgp_vm,glance_image'] = self.global_conf['glance,image_name']
              vn_info['bgp_vm,userdata'] = tenant_network_conf[i]['bgp_vm'].get('userdata',None)

            if tenant_network_conf[i].has_key('bms'):
              vn_info['bms,name']  = tenant_network_conf[i]['bms']['name']
              vn_info['bms,count'] = tenant_network_conf[i]['bms'].get('count',1)
              vn_info['bms,tor_list']   = tenant_network_conf[i]['bms']['tor_list']
            if tenant_network_conf[i].has_key('route_targets'):
              vn_info['route_target,count']     = tenant_network_conf[i]['route_targets']['count']
              vn_info['route_target,asn']       = tenant_network_conf[i]['route_targets']['asn']
              vn_info['route_target,rt_number'] = tenant_network_conf[i]['route_targets']['rt_number']
            if tenant_network_conf[i]['adv_options'].has_key('external_flag'):
              vn_info['external_flag'] = tenant_network_conf[i]['adv_options']['external_flag']
            else:
              vn_info['external_flag'] = False
            if tenant_network_conf[i]['adv_options'].has_key('extend_to_pr_flag') and tenant_network_conf[i]['adv_options']['extend_to_pr_flag']:
              vn_info['extend_to_pr_flag'] = True
            else:
              vn_info['extend_to_pr_flag'] = False
            self.tenant_conf['tenant,vn_group_list'].append(vn_info)

        tenant_vdns_conf = tenant_conf.get('vDNS',None)
        if tenant_vdns_conf:
           self.tenant_conf['vdns,name_pattern']         = tenant_vdns_conf['name']
           self.tenant_conf['vdns,domain_name,pattern']  = tenant_vdns_conf['domain_name']
           self.tenant_conf['vdns,dyn_updates']          = tenant_vdns_conf['dyn_updates']
           self.tenant_conf['vdns,rec_resolution_order'] = tenant_vdns_conf['rec_resolution_order']
           self.tenant_conf['vdns,floating_ip_record']   = tenant_vdns_conf['floating_ip_record']
           self.tenant_conf['vdns,ttl']                  = tenant_vdns_conf['ttl']
           self.tenant_conf['vdns,forwarder']            = tenant_vdns_conf['forwarder']
           self.tenant_conf['vdns,external_visible']     = tenant_vdns_conf['external_visible']
           self.tenant_conf['vdns,reverse_resolution']   = tenant_vdns_conf['reverse_resolution']

        tenant_ipam_conf = tenant_conf.get('IPAM',None)
        if tenant_ipam_conf:
           self.tenant_conf['ipam,name,pattern']  = tenant_ipam_conf['name']
           self.tenant_conf['ipam,count']         = tenant_ipam_conf['count']

        tenant_policy = tenant_conf.get('policies',None)
        if tenant_policy:
           self.tenant_conf['policy,name,pattern']        = tenant_policy['name']
           self.tenant_conf['policy,count']               = tenant_policy['count']
           self.tenant_conf['policy,allow_rules_network'] = tenant_policy['rules']['allow_rules_network']
           self.tenant_conf['policy,allow_rules_port']    = tenant_policy['rules']['allow_rules_port']
           
        tenant_fip = tenant_conf.get('FIP',None)
        if tenant_fip:
           self.tenant_conf['fip,name']            = tenant_fip['floating_ip_pool']
           self.tenant_conf['fip,gw_vn_count']     = tenant_fip['count']
           self.tenant_conf['fip,gw_vn_name']      = tenant_fip['fip_gw_vn_name']
           self.tenant_conf['fip,allocation_type'] = tenant_fip['alloc_type']
           self.tenant_conf['fip,count']           = tenant_fip['count']

        tenant_routers = tenant_conf.get('routers',None)
        if tenant_routers:
           tenant_router = tenant_conf['routers'][0]
           self.tenant_conf['routers,name']        = tenant_router['name']
           self.tenant_conf['routers,count']       = tenant_router['count']
        service_instance = tenant_conf.get('service_instance',None)
        if service_instance:
           self.tenant_conf['service_instances'] = service_instance
         
        tenant_traffic_block = self.test_conf.get('traffic_block',None)
        if tenant_traffic_block:
           url_short_file = '/opt/contrail/tools/http/httpload/url_short'
           url_lls_file = '/opt/contrail/tools/http/httpload/url_lls'
           url_lb_file = 'opt/contrail/tools/http/httpload/url_lb'
           run = '/opt/contrail/zmq/run'
           duration = int(tenant_traffic_block['duration'])
           sampling_interval = int(tenant_traffic_block['sampling_interval'])
           httpload_loop_count = duration // sampling_interval
           lls_rate = int(tenant_traffic_block['client_comm']['c_httpload_lls'][-1])
           short_rate = int(tenant_traffic_block['client_comm']['c_httpload_short'][-1])

           self.traffic_conf['duration'] = str(duration)
           self.traffic_conf['sampling_interval'] = str(sampling_interval)
           self.traffic_conf['external_server_ip'] = tenant_traffic_block['external_server']['ip']
           self.traffic_conf['pvn_ext_port_start'] = int(tenant_traffic_block['external_server']['pvn_ext_port_start'])
           self.traffic_conf['psvn_ext_port_start'] = int(tenant_traffic_block['external_server']['snat_ext_port_start'])
           self.traffic_conf['ping'] = tenant_traffic_block['client_comm']['c_ping']
           self.traffic_conf['c_iperf3'] = tenant_traffic_block['client_comm']['c_iperf3'] + ["-i", str(sampling_interval), "-t", str(duration)]
           self.traffic_conf['s_iperf3'] = tenant_traffic_block['server_comm']['s_iperf3']

           self.traffic_conf['httpload_lb'] = tenant_traffic_block['client_comm']['c_lbaas']

           self.traffic_conf['httpload_lls'] = [run, str(httpload_loop_count)] + tenant_traffic_block['client_comm']['c_httpload_lls'] + \
                                               ['-fetches', str(lls_rate * sampling_interval), url_lls_file]
           self.traffic_conf['httpload_short'] = [run, str(httpload_loop_count)] + tenant_traffic_block['client_comm']['c_httpload_short'] + \
                                               ['-fetches', str(short_rate * sampling_interval), url_short_file]

        


    def initTest(self,args):

        self.parse_config()
        tenant_name_list = self.parse_cli_args(args)
        self.global_conf['tenant_name_list'] = tenant_name_list

        self.testbed_file    = self.ini_global_conf['ENV']['testbed_file']

    def configure_global_config(self):

        tenant_name_list = self.global_conf['tenant_name_list']
        conn_obj_list = self.conn_obj_list

        func_arg = conn_obj_list,self.thread_count,self.global_conf,self.tenant_conf
        #svc_obj = ServiceTemplateConfig(None)
        #svc_obj.create_service_templates(*func_arg)

        vdns_obj = vDNS(None)
        vdns_obj.create_mgmt_vdns_tree(*func_arg)

        mgmt_vn_fqname,mgmt_vn_uuid = create_mgmt_vn_ipam(*func_arg)

        router_obj = RouterConfig(None)
        router_obj.create_physical_routers(*func_arg)

        pr_mx_name_list = []
        pr_mxs = self.global_conf['pr_mx']
        for pr_mx in pr_mxs:
            pr_mx_name_list.append(pr_mx['name'])

        kwargs = {}
        kwargs['tenant_name'] = 'admin'
        kwargs['vn_name']     = self.global_conf['mgmt,vn_name']
        kwargs['router_list'] = pr_mx_name_list
        kwargs['vn_ids']      = [mgmt_vn_uuid]
        kwargs['fq_name']     = [mgmt_vn_fqname]
        pr_obj_list = []
        vn_obj = VN(None)
        for router_name in pr_mx_name_list:
            pr_obj = vn_obj.retrieve_pr_obj(conn_obj_list=conn_obj_list,router_name=router_name)
            if pr_obj:
               pr_obj_list.append(pr_obj)
        mgmt_vn_obj = VN(None)
        for pr_obj in pr_obj_list:
            mgmt_vn_obj.add_extend_to_pr(count=self.thread_count,conn_obj_list=conn_obj_list,pr_obj=pr_obj,**kwargs)

        lls_obj = LLS(None)
        lls_obj.create_link_local_services(*func_arg)
 
        router_obj = RouterConfig(None)
        router_obj.create_tors(*func_arg)
        router_obj.create_physical_interfaces(*func_arg)

        global_conf_obj = VrouterGlobalConfig(None)
        global_conf_obj.update_conf(count=self.thread_count,conn_obj_list=conn_obj_list)

    def configure_tenant(self):
        tenant_name_list_conf = self.global_conf['tenant_name_list']
        conn_obj_list=self.conn_obj_list

        func_arg = conn_obj_list,self.thread_count,self.global_conf,self.tenant_conf,tenant_name_list_conf

        #svc_obj = ServiceTemplateConfig(None)
        #svc_obj.create_service_instances(*func_arg)
        #return

        project_obj = ProjectConfig(None)
        project_obj.create_tenants(*func_arg)

        tenant_name_list = []
        existing_tenants = project_obj.retrieve_configured_tenant_list(conn_obj_list=conn_obj_list)
        for tenant_name in tenant_name_list_conf:
            if tenant_name in existing_tenants:
               tenant_name_list.append(tenant_name)

        func_arg = conn_obj_list,self.thread_count,self.global_conf,self.tenant_conf,tenant_name_list

        policy_obj = Policy(None)
        policy_obj.create_policies(*func_arg)
        vdns_obj = vDNS(None)
        vdns_obj.create_data_vdns_tree(*func_arg)
        ipam_obj = IPAM(None)
        ipam_obj.create_ipams(*func_arg)

        vn_obj = VN(None)
        vn_obj.create_vns(*func_arg)

        #svc_obj = ServiceTemplateConfig(None)
        #svc_obj.create_service_instances(*func_arg)
        #return

        lrouter_obj = LogicalRouterConfig(None)
        lrouter_obj.create_logical_routers(*func_arg)
        lrouter_obj.attach_vns_to_logical_routers(*func_arg)

        project_obj = ProjectConfig(None)
        project_obj.update_security_groups(*func_arg)

        vm_obj = VM(None)
        vm_obj.create_vms(*func_arg)
        
        fip_obj = FloatingIPPool(None)
        fip_obj.delete_fip_pools(*func_arg)
        fip_obj = FloatingIPPool(None)
        fip_obj.create_fip_pools(*func_arg)

        fip_obj = FloatingIPPool(None)
        fip_obj.associate_fips(*func_arg)

        router_obj = RouterConfig(None)
        router_obj.create_logical_interfaces(*func_arg)
        router_obj.associate_fip_to_vmis(*func_arg)

        lbaas_obj = Lbaas(None)
        lbaas_obj.create_lb_pools(*func_arg)
        lbaas_obj.create_lb_members(*func_arg)
        lbaas_obj.create_health_monitors(*func_arg)
        lbaas_obj.associate_health_monitors(*func_arg)
        lbaas_obj.create_lb_vips(*func_arg)
        lbaas_obj.associate_fip_to_vips(*func_arg)

        #bgpaas_obj = Bgpaas(None)
        #bgpaas_obj.create_bgpaas(*func_arg)

        time.sleep(5)

def main():

   parser = argparse.ArgumentParser(add_help=False)
   parser.add_argument("-i", "--ini_file", default=None,help="Specify global conf file", metavar="FILE")
   parser.add_argument("-c", "--yaml_config_file", default=None,help="Specify Test conf file", metavar="FILE")
   parser.add_argument('--delete',action="store_true",default=False,help='action for specific tenant only')
   parser.add_argument('--create',action="store_true",default=False,help='action for specific tenant only')
   parser.add_argument('--delete_global',action="store_true",default=False,help='action for specific tenant only')
   parser.add_argument('--create_global',action="store_true",default=False,help='action for specific tenant only')
   parser.add_argument('--tenant_count',action="store", default='0', help='action for specific tenant only')
   parser.add_argument('--tenant_index_range',action="store", default="0:650", help='action for specific tenant only')
   parser.add_argument('--tenant_index_random',action="store_true", default=False, help='action for specific tenant only')
   parser.add_argument('--tenant_name',action="store", default=None, help='action for specific tenant only[None or all or specific tenant_name]')
   parser.add_argument('--tenant_name_prefix',action="store", default=None, help='action for specific tenant only')
   parser.add_argument('--dry',action="store_true", default=False, help='action for specific tenant only')
   parser.add_argument('--traffic',action="store_true", default=False, help='action for specific tenant only')
   parser.add_argument('--traffic_only',action="store_true", default=False, help='action for specific tenant only')

   args, remaining_argv = parser.parse_known_args(sys.argv[1:])
   cli_args = parse_cli(remaining_argv)
   ini_conf = parse_cfg_file(args.ini_file)

   yaml_conf = parse_yaml_cfg_file(args.yaml_config_file)

   print args
      
   yaml_global_conf = yaml_conf['global_config']

   tests = yaml_conf['tests']
   for test_conf in tests:
      test_obj = Test(yaml_global_conf,ini_conf,test_conf)
      test_obj.initTest(args)
      tenant_name_list = test_obj.global_conf['tenant_name_list']
      if args.dry:
         print "##### TEST_ACTION ####"
         print "tenant_name_list:",tenant_name_list
         print "create:",args.create
         print "delete:",args.delete
         print "######################"
         continue
      
      if args.traffic_only:
           args.delete = False
           args.delete_global = False
           args.create_global = False
           args.create = False
           args.traffic = True
      if args.delete:
         test_obj.cleanup_tenant()
      if args.delete_global:
         test_obj.cleanup_global_config()
      if args.create_global:
         test_obj.configure_global_config()
      if args.create:
         test_obj.configure_tenant()
      if args.traffic:
         fp = open("result.txt","w")
         print time.time()
         tenants = test_obj.get_vm_info()
         print time.time()
         print "checking MGMT IP reachability..."
         import pdb; pdb.set_trace()
         if not mgmt_ip_reachable(tenants):
            print "MGMT IP not pingable"
            fp.write("1")
            sys.exit()
         kill_result = build_kill_traffic_commands(test_obj, tenants)
         bms_vlans = test_obj.get_vlan_info()
         print time.time()
         if bms_vlans:
            cleanup_bms_netns(test_obj.global_conf['pr_qfx'], bms_vlans)
            if not setup_bms_netns(test_obj.global_conf['pr_qfx'], bms_vlans):
               print "BMS NETNS setup failed"
               sys.exit()
         #redo_dhclient(tenants)
         if test_obj.traffic_conf:
            print "Running Feature PINGs. Results in ping_result.log"
            if ping_check_setup(test_obj, tenants):
               print "Feature Ping Passed. Running FULL Traffic"
               client_res = run_traffic(test_obj, tenants)
               kill_result = build_kill_traffic_commands(test_obj, tenants)
               fp.write("0")
            else:
               print "Feature Ping Failed. Exiting"
               fp.write("1")
   print "Exiting test"
main()
