# Aviatrix Python SDK Generator

Generating the SDK requires that you have access to the Aviatrix API Documentation Postman Collection json file from the Aviatrix support portal. The file is located here: <https://support.aviatrix.com/apiDownloads> and requires a support account.

## How to generate SDK

1. Download the Postman collection file from <https://support.aviatrix.com/apiDownloads>.
2. Install the SDK generator library.

```Bash
python -m pip install git+https://github.com/Jeramy-Wilcox/Aviatrix-Python-SDK-Generator.git
```

3. Run the SDK generator using the CLI command.

```Bash
generate-aviatrix-sdk -f <path/to/Postman_collection_file> -o <path/to/generated_sdk_output_dir>
```

The Generator CLI command takes two optional arguments.

- **-f** OR **--api_file_path**: This is the path to the Postman collection file that you downloaded. The path should include the filename.
- **-o** OR **--output_dir**: This is the directory where the SDK will be built. It will default to the directory where the CLI command was ran.
