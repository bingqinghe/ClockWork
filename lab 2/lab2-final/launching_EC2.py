from boto import ec2

AWS_ACCESS_KEY_ID = "AKIAIGLXRUP2V7HEJ6WA"
AWS_SECRET_ACCESS_KEY = "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"

conn = ec2.connect_to_region('us-east-1', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

# Key pair creation
kp = conn.create_key_pair('MyKeyPair3')

# Save key-pair
kp.save('./')

# Create security group for HTTP, SSH and Pinging
security_groups = conn.create_security_group('csc326-groupg326-1-007', 'CSC326 project group g326-1-007')

# To ping the server
security_groups.authorize('ICMP', from_port=-1, to_port=-1, cidr_ip = '0.0.0.0/0')

# To allow SSH
security_groups.authorize('TCP', from_port=22, to_port=22, cidr_ip = '0.0.0.0/0')

# To allow HTTP
security_groups.authorize('TCP', from_port=80, to_port=80, cidr_ip = '0.0.0.0/0')

# Get security groups
sec_groups = conn.get_all_security_groups()
#print sec_groups[0]

# Launch a new instance:
conn.run_instances('ami-b93164ae', key_name='MyKeyPair3', instance_type = 't2.micro', security_groups=sec_groups)

reservations = conn.get_all_reservations()
instances = reservations[0].instances
inst = instances[0]

print inst.instance_type
print inst.placement

# Allocate an elastic ip
#addr = conn.allocate_address()

# Associate addr with running instance
#addr.associate(instance_id=inst.id)