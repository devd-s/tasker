# Database Considerations

As mentioned in task everything is running on cloud provider so I would go ahead with RDS creation using terraform and for the sake of this task I am creating STS with minimal configuration for which postgres.yaml is created as limitation of local system resources. 

## Considerations for rds using terraform 

Database Instance Type:

    Choose an appropriate instance type based on your workload requirements (e.g., db.m5.large for medium-scale workloads).
    Ensuring enough CPU, memory, and storage to handle your application's needs.

High Availability:

    Enable Multi-AZ deployments for production databases to ensure high availability and automatic failover.
    For redundancy in case of an Availability Zone (AZ) failure.

Backup and Retention:

    By default enabling automated backups and specify the retention period (e.g., 7 or 14 days).
    Creating manual snapshots before major changes or deployments.

Security:

    Use VPC: Ensuring the RDS instance is placed inside a private subnets).
    Encryption: Enable encryption at rest and in transit (SSL/TLS) to secure your data and also using kms key for encryption
    IAM Authentication: enabling IAM database authentication to avoid hardcoding credentials and for which secrets-store-csi-driver is required to mount secrets from AWS secrets manager.
    Security Groups: Controling access using security groups to allow traffic only from your EKS cluster or trusted IPs.

Parameter and Option Groups:

    Using custom parameter groups to optimize performance based on your workload (e.g., adjusting connection limits, query cache, etc.). Using secrets-store-csi-driver to mount secrets from AWS Secrets Manager directly into Kubernetes pods.
    
Scaling:

    Set up Auto Scaling for read replicas or scale the instance type based on load.
    Using Provisioned IOPS for high-performance workloads.

Monitoring:

    Enhanced Monitoring and CloudWatch metrics to monitor key performance indicators (e.g., CPU, memory, disk I/O).
    Setting up CloudWatch Alarms to notify team when performance degrades or thresholds are reached.

## When running as STS in Kubernetes following components are required in production

1. Storage Class to provision storage.
2. Persistent Volumes
3. Persistent VolumeClaims
4. Configmap to tweak postgres configuration
5. Secret for db access
6. Stateful set, Service, Pod disruption Budget and network policy to restrict access 

I have not created all components but these all should be considered for creation.

