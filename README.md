# Restaurant Customer Service Agents

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![NextJS](https://img.shields.io/badge/Built_with-NextJS-blue)
![OpenAI API](https://img.shields.io/badge/Powered_by-OpenAI_API-orange)

This repository contains a demo of a Customer Service Agent interface built on top of the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).
It is composed of two parts:

1. A python backend that handles the agent orchestration logic, implementing the Agents SDK

2. A Next.js frontend providing a chat interface.

## How to use

### Setting your env

You can set your environment variables by running the following command in your terminal:

```bash
export OPENAI_API_KEY=your_api_key
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_DB=2
```

or:

```bash
cp .env.example .env
```

### Install dependencies

Install the dependencies for the backend by running the following commands:

#### Using Poetry

```bash
cd backend
poetry install 
```

#### Using pip

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Activate it (use source .venv/bin/activate on linux/macOS)
pip install -r requirements.txt
```

#### Using Docker Compose

```bash
cd backend
docker-compose up --build
```

For the frontend, you can run:

```bash
cd frontend
npm install
```

### Running the app

#### Run the backend (without Docker)

From the `backend` folder, run:

```bash
poetry run uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

or :

```bash
python -m uvicorn api:app --reload --port 8000
```

The backend will be available at: [http://localhost:8000](http://localhost:8000)

#### Run the frontend

From the `frontend` folder, run:

```bash
npm run dev
```

The frontend will be available at: [http://localhost:3000](http://localhost:3000)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
