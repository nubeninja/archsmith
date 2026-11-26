# Shapes

Official shapes only. Names below rendered correctly before. Check any other name with the draw.io MCP `search_shapes` tool when it is connected. Never invent a shape name.

- AWS: `mxgraph.aws4.*` only. GitHub: `mxgraph.weblogos.github`. People:
  `mxgraph.aws4.authenticated_user` or `resIcon=mxgraph.aws4.client`.
- No Kubernetes shapes, no clip art, no image URLs. Show in-cluster parts with AWS
  icons: pods `container_1`, Deployment `container_3`, HPA and Cluster Autoscaler
  `auto_scaling2`, Load Balancer Controller and TargetGroupBinding
  `application_load_balancer`, VPC CNI `elastic_network_interface`, CoreDNS `cloud_map`,
  Pod Identity `identity_and_access_management`, CSI driver `secrets_manager`,
  CloudWatch agent `cloudwatch_2`.
  - resourceIcon: route_53, api_gateway, waf, eks, aurora, ecr, secrets_manager,
    identity_and_access_management, cloudwatch_2, key_management_service, auto_scaling2,
    cloud_map, vpc_privatelink, ec2, client
  - plain shapes: application_load_balancer, nat_gateway, endpoints,
    elastic_network_interface, aurora_instance, bucket, certificate_manager,
    container_1/2/3, internet_alt2, authenticated_user
  - groups: group_aws_cloud_alt, group_region, group_vpc2, group_availability_zone,
    group_security_group (subnets), group_auto_scaling_group, group_ec2_instance_contents
