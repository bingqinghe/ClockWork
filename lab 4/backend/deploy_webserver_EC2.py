from boto import ec2
import os
import time

URLS = "./uoft.txt"
DATABASE = "./uoft.db"

# Access keys defined in the file ~./boto like the following:
# [Credentials]
# aws_access_key_id = YOURACCESSKEY
# aws_secret_access_key = YOURSECRETKEY

def launch_EC2_instance():
	
	conn = ec2.connect_to_region('us-east-1')

	# Key pair creation	and save key-pair
	
	if os.path.isfile('./MyKeyPairNew.pem') is False:
		kp = conn.create_key_pair('MyKeyPairNew')
		kp.save('./')		

	# Create security group for HTTP, SSH and Pinging
	security_groups = -1
	try:
		security_groups = conn.get_all_security_groups(groupnames = ['csc326-groupg326-1-007'])
		security_groups = security_groups[0]
	except:
		security_groups = conn.create_security_group('csc326-groupg326-1-007', 'CSC326 project group g326-1-007')

		# To ping the server	# To allow SSH 	# To allow HTTP
		security_groups.authorize('ICMP', from_port=-1, to_port=-1, cidr_ip = '0.0.0.0/0')
		security_groups.authorize('TCP', from_port=22, to_port=22, cidr_ip = '0.0.0.0/0')
		security_groups.authorize('TCP', from_port=80, to_port=80, cidr_ip = '0.0.0.0/0')

	# Get security groups
	sec_groups = conn.get_all_security_groups()
	#print sec_groups[0]

	# Launch a new instance:
	res = conn.run_instances('ami-b93164ae', key_name='MyKeyPairNew', instance_type = 't2.micro', security_groups=sec_groups)

	# allocate a static ip address to the instance
	addrs = conn.get_all_addresses()
	addr = 0
	if len(addrs) == 0:
		addr = conn.allocate_address()
	else:
		addr = addrs[0]	

	instances = res.instances
	inst = instances[0]
	print "Instance status: " + inst.state
	while inst.state != "running":
		time.sleep(10)
		inst.update()

	addr.associate(instance_id=inst.id)

	return addr, inst.id

def deploy_EC2_instance():

	print "Deployment script: launching an EC2 instance and associating it with an Elastic IP..."
	ip_address, instance_id = launch_EC2_instance()
	# except:
	# 	print "Cannot launch an EC2 instance due to errors."
	# 	return -1


	ip_excluded = ip_address.public_ip

	print "Deployment script: Copying search engine to EC2 instance..."
	#os.system("scp -o StrictHostKeyChecking=no -i MyKeyPairNew.pem -r ./ ubuntu@%s:~/" % ip_excluded) 
	os.system("rsync -avz -e 'ssh -o StrictHostKeyChecking=no -i MyKeyPairNew.pem' ../ ubuntu@%s:~/" % ip_excluded)
	
	print "Deployment script: Installing dependencies and starting search webserver..."
	#dependencies = "sudo apt-get -y update && sudo apt-get -y install python && sudo apt-get -y install python-dev && sudo apt-get -y install python-pip && sudo pip install autocorrect && sudo pip install pyparsing"
	#dependencies = dependencies +  " && sudo pip install bottle && sudo pip install beaker && sudo pip install oauth2client && sudo pip install google-api-python-client && sudo pip install httplib2"
	#dependencies = dependencies + " && sudo pip install paste && sudo /bin/sh -c cd /frontend && ls -l && sudo nohup python webserver.py"
	dependencies = "sudo apt-get -y update; sudo apt-get -y install python; sudo apt-get -y install python-dev; sudo apt-get -y install python-pip; sudo pip install autocorrect; sudo pip install pyparsing"
	dependencies = dependencies +  "; sudo pip install bottle; sudo pip install beaker; sudo pip install oauth2client; sudo pip install google-api-python-client; sudo pip install httplib2"
	dependencies = dependencies + "; sudo apt-get -y install python-tk; sudo pip install matplotlib; sudo pip install mpld; sudo pip install jinja2"
	dependencies = dependencies + "; sudo pip install paste; cd frontend; ls -l; sudo nohup python webserver.py"
	os.system("ssh -o StrictHostKeyChecking=no -i MyKeyPairNew.pem ubuntu@%s '%s'" % (ip_excluded, dependencies))


	print "Deployment script: Finished. Instance id %s deployed at: \n" % instance_id
	print "IP ", ip_address

	return ip_address, instance_id


deploy_EC2_instance()

