import os


class Config:
    @property
    def neo4j_host(self):
        return os.getenv('NEO4J_HOST', 'bolt://localhost:7687')

    @property
    def neo4j_user(self):
        return os.getenv('NEO4J_USER', 'neo4j')

    @property
    def neo4j_pass(self):
        return os.getenv('NEO4J_PASS', 'pass')

    @property
    def neo4j_auth(self):
        return self.neo4j_user, self.neo4j_pass
