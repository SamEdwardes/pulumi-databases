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

    def __init__(self, name: str):
        self.name = name
        self.config = pulumi.Config()
        self.tags = self.config.get_object("tags")
        self.security_group = self.create_security_group()
        self.database = self.create_database()

    def create_security_group(self) -> ec2.SecurityGroup:
        return ec2.SecurityGroup(
            f"Security Group - {self.name}",
            description=self.tags["rs:owner"]
            + " security group for Pulumi MariaDB deployment.",
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
            tags=self.tags
            | {"Name": f"mariadb-{self.tags['rs:owner']}-security-group"},
        )

    def create_database(self):
        """
        Create a MariaDB database.
        """
        db = rds.Instance(
            self.name,
            instance_class="db.t3.micro",
            allocated_storage=20,
            username=self.config.get_object("mariadb")["username"],
            password=self.config.get_object("mariadb")["password"],
            db_name=self.config.get_object("mariadb")["database_name"],
            engine="mariadb",
            publicly_accessible=True,
            skip_final_snapshot=True,
            tags=self.tags | {"Name": f"mariadb-{self.tags['rs:owner']}-database"},
            vpc_security_group_ids=[self.security_group.id],
        )

        pulumi.export("mariadb_port", db.port)
        pulumi.export("mariadb_address", db.address)
        pulumi.export("mariadb_endpoint", db.endpoint)
        pulumi.export("mariadb_name", db.name)
        pulumi.export("mariadb_domain", db.domain)
        return db


class PostgreSQL:
    database: rds.Instance
    security_group: ec2.SecurityGroup

    def __init__(self, name: str):
        self.name = name
        self.config = pulumi.Config()
        self.tags = self.config.get_object("tags")
        self.security_group = self.create_security_group()
        self.database = self.create_database()

    def create_security_group(self) -> ec2.SecurityGroup:
        return ec2.SecurityGroup(
            f"Security Group - {self.name}",
            description=self.tags["rs:owner"]
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
            tags=self.tags
            | {"Name": f"postgres-{self.tags['rs:owner']}-security-group"},
        )

    def create_database(self):
        """
        Create a PostgreSQL database.
        """
        db = rds.Instance(
            self.name,
            instance_class="db.t3.micro",
            allocated_storage=5,
            username=self.config.get_object("postgres")["username"],
            password=self.config.get_object("postgres")["password"],
            db_name=self.config.get_object("postgres")["database_name"],
            engine="postgres",
            publicly_accessible=True,
            skip_final_snapshot=True,
            tags=self.tags | {"Name": f"postgres-{self.tags['rs:owner']}-database"},
            vpc_security_group_ids=[self.security_group.id],
        )

        pulumi.export("postgres_port", db.port)
        pulumi.export("postgres_address", db.address)
        pulumi.export("postgres_endpoint", db.endpoint)
        pulumi.export("postgres_name", db.name)
        pulumi.export("postgres_domain", db.domain)
        return db


if __name__ == "__main__":
    main()
