from typing import Dict

import pulumi
from pulumi_aws import ec2, rds


def main():
    config = pulumi.Config()
    if config.require_object("mariadb")["create"]:
        mariadb = MariaDB("mariadb")
    if config.require_object("postgres")["create"]:
        postgres = PostgreSQL("postgres")


class MariaDB:
    database: rds.Instance
    security_group: ec2.SecurityGroup

    def __init__(self, pulumi_name: str):
        self.pulumi_name = pulumi_name
        # Get and set config values.
        config = pulumi.Config()
        self.db_username: str = config.require_object("mariadb")["username"]
        self.db_password: str = config.require_object("mariadb")["password"]
        self.db_name: str = config.require_object("mariadb")["database_name"]
        # AWS tags.
        self.aws_tags: Dict = config.require_object("aws_tags")
        self.owner: str = self.aws_tags["rs:owner"]
        # Create infrastructure.
        self.security_group = self.create_security_group()
        self.database = self.create_database()

    def create_security_group(self) -> ec2.SecurityGroup:
        return ec2.SecurityGroup(
            f"Security Group - {self.pulumi_name}",
            description=self.owner + " security group for Pulumi MariaDB deployment.",
            ingress=[
                {
                    "protocol": "TCP",
                    "from_port": 3306,
                    "to_port": 3306,
                    "cidr_blocks": ["0.0.0.0/0"],
                    "description": "MariaDB",
                },
            ],
            egress=[
                {
                    "protocol": "All",
                    "from_port": -1,
                    "to_port": -1,
                    "cidr_blocks": ["0.0.0.0/0"],
                    "description": "Allow all outbound traffic",
                },
            ],
            tags=self.aws_tags | {"Name": f"mariadb-{self.owner}-security-group"},
        )

    def create_database(self):
        """
        Create a MariaDB database.
        """
        db = rds.Instance(
            self.pulumi_name,
            instance_class="db.t3.micro",
            allocated_storage=20,
            username=self.db_username,
            password=self.db_password,
            db_name=self.db_name,
            engine="mariadb",
            publicly_accessible=True,
            skip_final_snapshot=True,
            tags=self.aws_tags | {"Name": f"mariadb-{self.owner}-database"},
            vpc_security_group_ids=[self.security_group.id],
        )

        pulumi.export("mariadb_port", db.port)
        pulumi.export("mariadb_address", db.address)
        pulumi.export("mariadb_endpoint", db.endpoint)
        pulumi.export("mariadb_name", db.name)
        pulumi.export("mariadb_domain", db.domain)
        pulumi.export(
            "mariadb_r_connection", 
            pulumi.Output.all(
                db_address=db.address
            ).apply(
                lambda args: f'''con <- DBI::dbConnect(odbc::odbc(), Driver='mysql', Server = '{args["db_address"]}', Port = '3306', UID = '{self.db_username}', PWD = '{self.db_password}', Database = '{self.db_name}', timeout = 10)'''
            )
        )
        return db


class PostgreSQL:
    database: rds.Instance
    security_group: ec2.SecurityGroup

    def __init__(self, pulumi_name: str):
        self.pulumi_name = pulumi_name
        # Get and set config values.
        config = pulumi.Config()
        self.db_username: str = config.require_object("postgres")["username"]
        self.db_password: str = config.require_object("postgres")["password"]
        self.db_name: str = config.require_object("postgres")["database_name"]
        # AWS tags.
        self.aws_tags: Dict = config.require_object("aws_tags")
        self.owner: str = self.aws_tags["rs:owner"]
        # Create infrastructure.
        self.security_group = self.create_security_group()
        self.database = self.create_database()

    def create_security_group(self) -> ec2.SecurityGroup:
        return ec2.SecurityGroup(
            f"Security Group - {self.pulumi_name}",
            description=self.owner
            + " security group for Pulumi PostgreSQL deployment.",
            ingress=[
                {
                    "protocol": "TCP",
                    "from_port": 5432,
                    "to_port": 5432,
                    "cidr_blocks": ["0.0.0.0/0"],
                    "description": "PostgreSQL",
                },
            ],
            egress=[
                {
                    "protocol": "All",
                    "from_port": -1,
                    "to_port": -1,
                    "cidr_blocks": ["0.0.0.0/0"],
                    "description": "Allow all outbound traffic",
                },
            ],
            tags=self.aws_tags | {"Name": f"postgres-{self.owner}-security-group"},
        )

    def create_database(self):
        """
        Create a PostgreSQL database.
        """
        db = rds.Instance(
            self.pulumi_name,
            instance_class="db.t3.micro",
            allocated_storage=5,
            username=self.db_username,
            password=self.db_password,
            db_name=self.db_name,
            engine="postgres",
            publicly_accessible=True,
            skip_final_snapshot=True,
            tags=self.aws_tags | {"Name": f"postgres-{self.owner}-database"},
            vpc_security_group_ids=[self.security_group.id],
        )

        pulumi.export("postgres_port", db.port)
        pulumi.export("postgres_address", db.address)
        pulumi.export("postgres_endpoint", db.endpoint)
        pulumi.export("postgres_name", db.name)
        pulumi.export("postgres_domain", db.domain)
        pulumi.export(
            "postgres_r_connection", 
            pulumi.Output.all(
                db_address=db.address
            ).apply(
                lambda args: f'''con <- DBI::dbConnect(odbc::odbc(), Driver='postgresql', Server = '{args["db_address"]}', Port = '5432', UID = '{self.db_username}', PWD = '{self.db_password}', Database = '{self.db_name}', timeout = 10)'''
            )
        )
        return db


if __name__ == "__main__":
    main()
