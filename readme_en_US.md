# SimpleRAG

## Overview

SimpleRAG is a comprehensive tool designed to streamline the process of converting PDF documents into Markdown format and preparing them for Retrieval-Augmented Generation (RAG) applications. This tool provides a series of steps to convert, split, and process documents, including image handling and uploading.

## Features

- **PDF to Markdown Conversion**: Convert PDF files to Markdown using OCR for enhanced text extraction.
- **Markdown Splitting**: Automatically split Markdown files into manageable sections.
- **Image Processing**: Upload images to cloud storage or local servers using PicGO or AliOSS.
- **Logging and Reporting**: Detailed logging and summary reports for each processing step.
- **GUI Support**: User-friendly graphical interface for easy operation.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/chen571428/SimpleRAG.git
   cd SimpleRAG
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment for PDF to Markdown conversion:
   - Ensure you have `conda` installed.
   - Create and activate the necessary conda environments as specified in the scripts.

## Usage

### Command Line Interface

You can run the main processing script using the command line:

```bash
python main.py -i <input_directory> -o <output_directory> --steps 1 2 3 --uploader picgo
```

### Graphical User Interface

To use the GUI, run:

```bash
python SimpleRAG/Gui/gui.py
```

### Configuration

Configuration settings for uploaders can be managed in `config.json`. Use `config.template.json` as a template to create your configuration file.

### Logging

Logs are generated for each process and stored in the `logs` directory within the specified output directory. This includes detailed logs and summary reports.

## Code Structure

- **Conversion**: Handles PDF to Markdown conversion.
  - `step1_pdf_to_md.py`: Main conversion logic.
  - `pdf2md.py`: Helper script for conversion.

- **Processing**: Handles splitting and image processing.
  - `step2_split_md.py`: Splits Markdown files.
  - `step3_process_images.py`: Processes and uploads images.

- **Utilities**: Additional tools and utilities.
  - `logger.py`: Logging utilities.
  - `uploaders.py`: Uploader factory for PicGO and AliOSS.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to all contributors and the open-source community for their support and contributions.
