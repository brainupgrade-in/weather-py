# Weather-Py


## Description
Weather-Py is a Python microservice designed to provide temperature information for a given place. This microservice utilizes a weather API to fetch and serve the relevant data.

## Features
- Fetches temperature data for any specified location.
- Easy-to-use RESTful API interface.
- Containerized for easy deployment.

## Installation

Clone the repository:
```bash
git clone https://github.com/brainupgrade-in/weather-py.git
cd weather-py
```
## Usage

To use the Weather-Py service, send a request to the `/place/<name>` endpoint where `<name>` is the name of the place. For example, to get the weather for Bangalore:

```bash
curl http://localhost:port/place/Bangalore
```
Replace `localhost:port` with your server's address and port number.

## Deployment

The microservice is container-ready and can be deployed using Docker.

Build the Docker image:

```bash
docker build -t weather-py .
```
Run the Docker container:

```bash
docker run -p 8080:8080 weather-py
```
## Contributing

Contributions to Weather-Py are welcome! Please refer to the project's issues and pull request sections for more information.

## License

This project is licensed under the [MIT License](LICENSE).



## Contact

For any queries, please open an issue on the [GitHub repository](https://github.com/brainupgrade-in/weather-py).

