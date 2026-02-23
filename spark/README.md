# Spark Environment Setup on Google Cloud VM

This repository documents the steps I followed to provision a development environment on a Google Cloud Platform virtual machine. The goal was to build a Linux-based (Ubuntu) data science workspace leveraging Java, Apache Spark, PySpark, and Jupyter notebooks. This README is written with recruiters and collaborators in mind, showcasing my ability to perform infrastructure setup, remote development, and Python data tooling.

## ✅ Provisioning the VM
1. **Create a VM instance** in Google Cloud Console using an Ubuntu distribution.
2. **Enable SSH access** and connect via Visual Studio Code's Remote - SSH extension, allowing me to work as if the code were local.

## 🛠️ Installing Dependencies
Once connected to the Linux machine, I executed the following steps to prepare the environment:

### Java (OpenJDK)
```bash
# Download and extract OpenJDK 11
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
rm openjdk-11.0.2_linux-x64_bin.tar.gz

# Configure environment variables
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"
```
These variables were added to `~/.bashrc` so they are set automatically whenever a new terminal session opens.

### Apache Spark & PySpark
```bash
# Download and unpack Spark
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar xzfv spark-3.5.0-bin-hadoop3.tgz
rm spark-3.5.0-bin-hadoop3.tgz

# Update environment
export SPARK_HOME="${HOME}/spark/spark-3.5.0-bin-hadoop3"
export PATH="${SPARK_HOME}/bin:${PATH}"
```
Adding these exports to `~/.bashrc` enables the `pyspark` command anywhere in the terminal.

### Python, Jupyter, and Pandas
```bash
sudo apt update
sudo apt install -y python3-pip python3-pandas
pip3 install jupyter
```
I launched PySpark with Jupyter support using:
```bash
PYSPARK_DRIVER_PYTHON=jupyter \\
PYSPARK_DRIVER_PYTHON_OPTS="notebook" \\
$SPARK_HOME/bin/pyspark
```
This opened a notebook server directly tied to the Spark context.

## 🔄 Shell Configuration
The `.bashrc` file was updated to include:
```bash
# Java and Spark environment variables
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export SPARK_HOME="${HOME}/spark/spark-3.5.0-bin-hadoop3"
export PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${PATH}"
```
With these lines, every new shell session is ready for Spark development without manual configuration.

## 🎯 Outcome
This setup demonstrates proficiency in:
- Cloud infrastructure provisioning (GCP VM)
- Remote development using VS Code SSH
- Installing and configuring Java and Apache Spark on Ubuntu
- Integrating Spark with Python via PySpark and Jupyter
- Managing environment variables for reproducible workflows

Feel free to explore the notebooks or reach out if you'd like me to walk through the implementation in a live demo!

