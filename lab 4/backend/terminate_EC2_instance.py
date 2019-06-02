from boto import ec2


# instance_id = 'i-04ce780d6bd6ed7ca'

# Access keys defined in the file ~./boto like the following:
# [Credentials]
# aws_access_key_id = YOURACCESSKEY
# aws_secret_access_key = YOURSECRETKEY

def terminate_EC2_instance(instance_id=None):

	if instance_id is None:
		instance_id = raw_input("Please specify an instance_id: ")

	# Connect to AWS and terminate instance
	conn = ec2.connect_to_region('us-east-1')
	conn.terminate_instances(instance_ids=[instance_id])

	print conn.get_all_instance_status(instance_ids=[instance_id])

	# Check if instance terminated safely:
	if len(conn.get_all_instance_status(instance_ids=[instance_id])) == 0:
		print "Instance %s terminated safely." % instance_id
	else:
		print "Unable to find or terminate instance %s." % instance_id


#terminate_EC2_instance(instance_id="i-0fe3022969a195edb")