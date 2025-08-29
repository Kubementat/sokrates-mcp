# How to publish

```
PYPI_API_TOKEN="REPLACEME"

# publish to pypi test instance
uv publish --index testpypi --token "$PYPI_API_TOKEN"

# Test the test package
TEMP_DIR="~/tmp/test_sokrates_mcp"
mkdir -p $TEMP_DIR

cd $TEMP_DIR
uv venv
source .venv/bin/activate
uv pip install --index-url https://test.pypi.org/simple/ sokrates-mcp
uv run sokrates-mcp --help


# publish to prod instance
PYPI_API_TOKEN="REPLACEME"
uv publish --token "$PYPI_API_TOKEN"

# Test the published package
TEMP_DIR="~/tmp/test_sokrates_mcp_prd"
rm -r $TEMP_DIR
mkdir -p $TEMP_DIR

cd $TEMP_DIR
uv venv
source .venv/bin/activate
# install
uv pip install sokrates-mcp

# test server executable
uv run sokrates-mcp --help
```