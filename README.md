# Notion2GoogleTasks 📝➡️📋

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarcChen/Notion2GoogleTasks/blob/master/LICENSE) [![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/) 

## Table of Contents 📚
- [Overview](#overview)
- [Features](#features)
- [Why Use This?](#why-use-this)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Overview 🌐
Notion2GoogleTasks is a tool designed to seamlessly integrate **Notion** with **Google Tasks**, allowing users to synchronize their tasks across these platforms effortlessly. By automating the transfer of data, this application eliminates manual work and enhances productivity.

> Note: While there are services like Zapier that offer similar functionality <button class="citation-flag" data-index="4">, our goal is to provide a lightweight, customizable solution tailored specifically for power users who prefer direct control over their integrations.

## Features ✨
- Automatic synchronization between Notion and Google Tasks.
- Supports bi-directional syncing.
- Customizable mappings for fields such as titles, descriptions, due dates, etc.
- Lightweight and easy-to-use interface.

## Why Use This? 🤔
If you're looking for a straightforward method to keep your tasks organized across multiple platforms without relying on third-party services, then Notion2GoogleTasks might be exactly what you need! It offers flexibility and customization options not always available through pre-built integrations.

## Prerequisites 🔧
Before getting started, ensure you have the following installed:
- Python 3.x
- pip (Python package manager)
- A Google account with access to Google Tasks API
- A Notion account with API access enabled

## Installation 💻
To install Notion2GoogleTasks, follow these steps:

1. Clone the repository: git clone https://github.com/MarcChen/Notion2GoogleTasks.git cd Notion2GoogleTasks
2. Install dependencies: `poetry install`
3. Configure your environment variables by copying `..env_template` to `.env` and filling out the necessary credentials.

## Usage 🚀
After installation, run the script via command line: `poetry run python main.py` with the exported `.env` vars.

## Configuration ⚙️
You can adjust various settings within the configuration file (`config.json`) to better suit your notion query preferences.

## Contributing 👥
We welcome contributions from everyone! Whether it's reporting bugs, suggesting improvements, or submitting pull requests, all help is appreciated. Please read our [Contribution Guidelines](CONTRIBUTING.md) before getting started.

## License 📜
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏
Special thanks to the communities behind:
- [Notion API Documentation](https://developers.notion.com/)
- [Google Tasks API](https://developers.google.com/tasks/quickstart/python)
