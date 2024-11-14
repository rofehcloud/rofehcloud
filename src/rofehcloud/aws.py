import subprocess
import json

from rofehcloud.logger import log_message


def get_regions_with_resources():
    # Get list of all regions
    log_message("INFO", "Getting list of all regions")
    regions = json.loads(
        subprocess.check_output("aws ec2 describe-regions --output json", shell=True)
    )
    region_names = [region["RegionName"] for region in regions["Regions"]]

    # List to store regions with resources
    regions_with_resources = []

    # Check each region for resources in various services
    for region in region_names:
        log_message(
            "INFO",
            f"Checking region {region} for resources (EC2, RDS, EKS, ECS, DynamoDB, Lambda)",
        )
        resources_found = []

        # Check for EC2 instances
        if has_resources(f"aws ec2 describe-instances --region {region} --output json"):
            log_message("INFO", "Found EC2 instances")
            resources_found.append("EC2")

        # Check for RDS databases
        if has_resources(
            f"aws rds describe-db-instances --region {region} --output json"
        ):
            log_message("INFO", "Found RDS databases")
            resources_found.append("RDS")

        # Check for EKS clusters
        if has_resources(f"aws eks list-clusters --region {region} --output json"):
            log_message("INFO", "Found EKS clusters")
            resources_found.append("EKS")

        # Check for ECS clusters
        if has_resources(f"aws ecs list-clusters --region {region} --output json"):
            log_message("INFO", "Found ECS clusters")
            resources_found.append("ECS")

        # Check for DynamoDB tables
        if has_resources(f"aws dynamodb list-tables --region {region} --output json"):
            log_message("INFO", "Found DynamoDB tables")
            resources_found.append("DynamoDB")

        # Check for Lambda functions
        if has_resources(f"aws lambda list-functions --region {region} --output json"):
            log_message("INFO", "Found Lambda functions")
            resources_found.append("Lambda")

        if resources_found:
            regions_with_resources.append(region)

    return regions_with_resources


def has_resources(command):
    try:
        output = subprocess.check_output(command, shell=True)
        log_message("DEBUG", f"Command output: {output}")
        data = json.loads(output)
        # Check if any key in the JSON contains a non-empty list
        return any(
            data[key] for key in data if isinstance(data[key], list) and data[key]
        )
    except subprocess.CalledProcessError:
        # Handle exceptions, such as no resources found or no permissions
        return False
