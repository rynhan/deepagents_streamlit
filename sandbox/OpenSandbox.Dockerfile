FROM opensandbox/server:release-1.1.0

COPY sandbox/os-sandbox.toml /etc/opensandbox/config.toml

ENV SANDBOX_CONFIG_PATH=/etc/opensandbox/config.toml