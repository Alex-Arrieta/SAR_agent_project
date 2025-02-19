# Search and Rescue (SAR) Agent Framework - CSC 581

## Introduction

This framework is for CSC 581 students to develop intelligent agents supporting the AI4S&R project. Students can create specialized agents for various SAR roles such as those listed in this spreadsheet:

https://docs.google.com/spreadsheets/d/1QZK5HAdDC-_XNui6S0JZTbJH5_PbYJTp8_gyhXmz8Ek/edit?usp=sharing
https://docs.google.com/spreadsheets/d/11rBV9CbKNeQbWbaks8TF6GO7WcSUDS_-hAoH75UEkgQ/edit?usp=sharing

Each student or team will choose a specific role within the SAR ecosystem and implement an agent that provides decision support and automation for that role.

## Logistic Agent Description

This little agent here is a logistics helper agent. Right now it really is just a glorified grapher. It allows you to specify suppliers, transit hubs, and missions and the connections between them. All classes for the graph are found in logistics_agent.py (yes bad design, I'll fix it later). All graph items just expect a name when you initlalize them. To add connections call node.update_connections(other, weight). I didn't make this automatically bidirectional so you have to go the other way from the other node to do that. Suppliers provide goods (string like "Rope") and Missions request goods. Call agent.calculate_deliveries() to get a list of all shortest delivery paths (individually, I just run Dijkstras for each mission and supplier pair that have the same good(s)). Eventually this will support "real-time" analysis by tracking locations of items every time tick to responsivly reassign routes and goods. But for now at least you can build out a nice little graph that can have its node features updated and then recalculate the desired path. The output right now is literally just list of lists of objects but I'll set it up to pretty print at some point.

## Prerequisites

- Python 3.8 or higher
- pyenv (recommended for Python version management)
- pip (for dependency management)

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sar-project
```

2. Set up Python environment:
```bash
# Using pyenv (recommended)
pyenv install 3.8.0  # or your preferred version
pyenv local 3.8.0

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Obtain required API keys:
  1. OpenAI API key: Sign up at https://platform.openai.com/signup
- Update your `.env` file with the following:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
- Make sure to keep your `.env` file private and never commit it to version control.

## Project Structure

```
sar-project/
├── src/
│   └── sar_project/         # Main package directory
│       └── agents/          # Agent implementations
│       └── config/          # Configuration and settings
│       └── knowledge/       # Knowledge base implementations
├── tests/                   # Test directory
├── pyproject.toml           # Project metadata and build configuration
├── requirements.txt         # Project dependencies
└── .env                     # Environment configuration
```

## Development

This project follows modern Python development practices:

1. Source code is organized in the `src/sar_project` layout
2. Use `pip install -e .` for development installation
3. Run tests with `pytest tests/`
4. Follow the existing code style and structure
5. Make sure to update requirements.txt when adding dependencies

