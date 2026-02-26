import socket
import time
from typing import ClassVar, Self

from testcontainers.mongodb import MongoDbContainer as _MongoDbContainer


class MongoDbContainer(_MongoDbContainer):
    replica_set_name: ClassVar[str] = "rs"
    key_file_path: ClassVar[str] = "/tmp/mongodb-keyfile"

    def __init__(
        self,
        image: str = "mongo:latest",
        port: int = 27017,
        username: str | None = None,
        password: str | None = None,
        dbname: str | None = None,
        **kwargs,
    ):
        super().__init__(
            image=image,
            port=port,
            username=username,
            password=password,
            dbname=dbname,
            **kwargs,
        )
        self._with_replica_set = False

    def get_connection_url(self) -> str:
        connection_url = super().get_connection_url()
        return (
            f"{connection_url}/?replicaSet={self.replica_set_name}"
            if self._with_replica_set
            else connection_url
        )

    def with_replica_set(self) -> Self:
        self.port = self._get_available_port()
        self.with_bind_ports(container=self.port, host=self.port)
        self._command = [
            "bash",
            "-c",
            f"openssl rand -base64 756 > {self.key_file_path} && "
            f"chmod 400 {self.key_file_path} && "
            f"chown mongodb:mongodb {self.key_file_path} && "
            f"exec docker-entrypoint.sh mongod"
            f" --keyFile {self.key_file_path}"
            f" --replSet {self.replica_set_name}"
            f" --port {self.port}",
        ]
        self._with_replica_set = True

        return self

    def _connect(self) -> None:
        super()._connect()
        if self._with_replica_set:
            self._initialize_replica_set()

    def _initialize_replica_set(self) -> None:
        elapsed = 0
        timeout = 30
        interval = 1
        while True:
            exit_code, stdout = self.exec(
                f"mongosh "
                f"--username={self.username} "
                f"--password={self.password} "
                f"--eval=\"rs.initiate({{_id:'{self.replica_set_name}',members:[{{_id:0,host:'localhost:{self.port}'}}]}})\" "
                f"mongodb://localhost:{self.port}"
            )
            if not exit_code:
                break

            time.sleep(interval)
            elapsed += interval
            if elapsed > timeout:
                raise RuntimeError(f"Could not initiate replica set due to {stdout.decode()}")

    @staticmethod
    def _get_available_port() -> int:
        with socket.socket() as sock:
            sock.bind(("", 0))
            return sock.getsockname()[1]
