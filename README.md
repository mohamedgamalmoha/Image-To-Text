# Image To Text Extraction

This system is a RESTful API that takes an image file as input and returns the text content of the image as output. 
The system uses the Tesseract OCR engine to extract text from the image.\
The system uses JWT (JSON Web Token) for authentication. To use the system, you need to generate a JWT token by sending 
a POST request to the /auth/login endpoint with a valid username and password. 
The server will return a JWT token that you can use to authenticate subsequent requests by including it in the Authorization header of the request. In case of not having an account, it is possible ot register throw /auth/signup endpoint 


## Features

- Auth system (registration, login) based on jwt.
- Text extraction from image.


## Installation

1. Clone the repository:
   ```shell
   git clone https://github.com/mohamedgamalmoha/image-to-text-extraction.git
   ```
2. Install virtual environment package - outside project directory -, then activate it:
    ```shell
    pip install virtualenv
    virtualenv env 
    source env/bin/activate (Linux/Mac)
    env\Scripts\activate (Windows)
    ```
3. Navigate to project directory, then install the requirements of the project by running:
    ```shell
    cd src
    pip install -r requirements.txt
    ```
4. Run server, then got the local [url](http://127.0.0.1:5000/):
    ```shell
    python run.py 
    ```

If you faced any problems setting up this project **please** feel free to inform us.


## Usage

To use the system, follow these steps:

1. Start with server
   ```shell
   python app.py
   ```
2. Send a POST request to the /image-to-text endpoint with an image file as the image parameter. For example, using curl:
   ```shell
   curl -H "Authorization: Bearer <your_jwt_token>" -F "image=@/path/to/image.jpg" http://localhost:5000/image-to-text
   ```
   Note that you need to replace <your_jwt_token> with a valid JWT token. You can generate a JWT token by sending a POST request to the /auth/login endpoint with a valid email and password.
   ```shell
   curl -X POST -H "Content-Type: application/json" -d '{"email":"john@gmail.com", "password":"password123"}' http://localhost:5000/auth/login
   ```

3. The server will return a JSON object containing the text content of the image, as well as some additional metrics:
  ```json
  {
   "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
   "num_words": 15,
   "num_chars": 84,
   "image_size": "1920x1080",
   "language": "English",
   "avg_confidence": 90.3,
   "image_format": "JPEG",
   "dpi": 72,
   "extraction_time": 3.5,
   "hocr": "<!DOCTYPE html><html><head>...</html>"
  }
   ```
   here is the explanation of each field of results 
   - **text:** The text content of the image. 
   - **num_words:** The number of words in the text content. 
   - **num_chars:** The number of characters in the text content. 
   - **image_size:** The size of the input image in pixels.
   - **language:** The langauge of the image's content 
   - **avg_confidence:** The average confidence score of the OCR engine for the extracted text.
   - **image_format:** The file format of the input image.
   - **dpi:** The resolution of the input image in dots per inch (DPI).
   - **extraction_time:** The time taken to extract text from the image in seconds.
   - **hocr:** The HOCR output of the OCR engine, which contains additional information such as the position of each word in the image.


## Built With
This application was built with the help of ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture. ChatGPT provided natural language processing capabilities that were used to implement the image-to-text extraction feature.
For more information on ChatGPT and its capabilities, check out the [ChatGPT documentation](https://beta.openai.com/docs/guides/chat-gpt). To learn more about OpenAI and its mission to ensure that artificial intelligence benefits humanity, visit the [OpenAI website](https://openai.com/).

## Contributing
Contributions are welcome! Please open an issue or submit a pull request if you would like to contribute code changes or suggest new features.


## License
This project is licensed under [MIT License](https://opensource.org/licenses/MIT).

