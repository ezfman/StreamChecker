# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/app`, then pip install it to install the `streamCheck` CLI tool
WORKDIR /app
ADD . /app
RUN uv pip install . --system

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the application from the project CLI script
CMD ["streamCheck"]