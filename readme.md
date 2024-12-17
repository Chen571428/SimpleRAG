# SimpleRAG

## 概述

SimpleRAG 是一个综合工具，旨在简化将 PDF 文档转换为 Markdown 格式并为检索增强生成 (RAG) 应用程序做准备的过程。该工具提供了一系列步骤来转换、拆分和处理文档，包括图像处理和上传。

本项目基于[PDFdeal](https://github.com/Menghuan1918/pdfdeal)，对其进行了包装，并增加了MinerU、Marker作为开源PDF处理后端，优化了部分功能，提供了一键运行的选项

## 功能

- **PDF 转 Markdown 转换**：使用 OCR 将 PDF 文件转换为 Markdown，以增强文本提取。
- **Markdown 拆分**：自动将 Markdown 文件拆分为可管理的部分。
- **图像处理**：使用 PicGO 或 AliOSS 将图像上传到云存储或本地服务器。
- **日志记录和报告**：为每个处理步骤提供详细的日志记录和总结报告。
- **GUI 支持**：用户友好的图形界面，便于操作。

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/chen571428/SimpleRAG.git
   cd SimpleRAG
   ```

2. 使用Conda提供虚拟环境，安装依赖
由于MinerU和Marker依赖的环境不同，所以需要使用Conda配置不同的环境
   ```python
   conda create -n SimpleRAG python=3.12 pip
   conda activate SimpleRAG
   pip install -r requirements_SimpleRAG.txt
   conda deactivate
   conda create -n MinerU python=3.12 pip
   conda activate MinerU
   pip install -r requirements_MinerU.txt
   conda deactivate
   ```
在此处完成配置的基础上，仍然需要参考[MinerU](https://github.com/Menghuan1918/MinerU)的文档，完成CUDA、cuDNN、模型文件下载、模型权重配置。

3. 确保环境可用
    ```python
    conda run --no-capture-output -n SimpleRAG marker_single --help
    conda run --no-capture-output -n MinerU magic-pdf -v
    ``` 
   如果输出不合理请重新配置

4. 配置PicGO 
    请自行下载PicGO
    根据[PicGO](https://picgo.github.io/PicGo-Doc/zh/guide/config.html)配置PicGO






## 使用方法

### 命令行界面

您可以使用命令行运行主处理脚本：
```bash
usage: main.py [-h] -i INPUT_DIR -o OUTPUT_DIR [--steps {1,2,3} [{1,2,3} ...]] [--uploader {picgo,alioss}] [--picgo-endpoint PICGO_ENDPOINT] [--oss-key-id OSS_KEY_ID] [--oss-key-secret OSS_KEY_SECRET]
               [--oss-endpoint OSS_ENDPOINT] [--oss-bucket OSS_BUCKET] [--config CONFIG] [--create-config] [--qps QPS] [--process-each] [--converter {marker,mineru}]

Convert PDFs to Markdown and preprocess for RAG applications

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Directory containing PDF files
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Directory for output files
  --steps {1,2,3} [{1,2,3} ...]
                        Specify which steps to run (1: PDF to MD, 2: Split MD, 3: Process Images). Example: --steps 1 3
  --uploader {picgo,alioss}
                        Image uploader type (default: picgo)
  --picgo-endpoint PICGO_ENDPOINT
                        PicGO server endpoint (default: http://127.0.0.1:36677)
  --oss-key-id OSS_KEY_ID
                        Aliyun OSS access key ID
  --oss-key-secret OSS_KEY_SECRET
                        Aliyun OSS access key secret
  --oss-endpoint OSS_ENDPOINT
                        Aliyun OSS endpoint
  --oss-bucket OSS_BUCKET
                        Aliyun OSS bucket name
  --config CONFIG       Path to config file (default: search in current directory and user home)
  --create-config       Create a default config file in current directory
  --qps QPS             Maximum queries per second for image upload (0 for no limit)
  --process-each        Process each PDF file immediately after conversion
  --converter {marker,mineru}
                        PDF to Markdown converter to use (default: marker)
```
#### 示例
```bash
python ..\OneStepPreForRAG\main.py -i /path/to/<input_directory> -o /path/to/<output_directory> --qps 600 --converter mineru --process-each --config ..\OneStepPreForRAG\config.json --uploader picgo
```

### 图形用户界面

要使用 GUI，参看OneStepPreForRAG/Gui/gui.py
```python
python OneStepPreForRAG/Gui/gui.py
```

### 配置

上传器的配置设置可以在 `config.json` 中管理。使用 `config.template.json` 作为模板创建您的配置文件。

### 日志记录

每个过程的日志会生成并存储在指定输出目录内的 `logs` 目录中。这包括详细的日志和总结报告。

## 代码结构

- **转换**：处理 PDF 到 Markdown 的转换。
  - `step1_pdf_to_md.py`：主要转换逻辑。
  - `pdf2md.py`：转换的辅助脚本。

- **处理**：处理拆分和图像处理。
  - `step2_split_md.py`：拆分 Markdown 文件。
  - `step3_process_images.py`：处理和上传图像。

- **实用工具**：附加工具和实用程序。
  - `logger.py`：日志记录实用程序。
  - `uploaders.py`：PicGO 和 AliOSS 的上传器工厂。

## 贡献

欢迎贡献！请 fork 仓库并提交 pull request 以进行任何改进或错误修复。

## 许可证

该项目根据 MIT 许可证授权。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 致谢

感谢PDFdeal、MinerU、Marker等成熟的开源项目
