# Products Comparer


## Installation

You can install Comparer using pip:

```bash
pip install .
```

## Usage

After installation, you can use the following commands:

```bash
# For apply migrations
comparer-db revision --autogenerate
comparer-db upgrade head
	
# For run app
comparer-api       
```

## Requirements

Make sure you have all the requirements installed by running:

```bash
pip install -r requirements.txt
```

## Docker

To run Comparer using Docker, navigate to the directory containing the `docker-compose.yml` file and run:

```bash
docker-compose up -d
```

