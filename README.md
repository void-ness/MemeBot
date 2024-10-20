## 🎉 Welcome to MemeBot

MemeBot is a simple Flask-based project designed to create hilarious memes in the format "pov: my music taste". Users can add four YouTube video URLs, and the meme generator will create a video out of them. Ready to make some memes? Let's get started! 😎

## 🚀 Features

- **Meme Generation**: Create memes using user-provided YouTube video URLs. 🎥
- **Video Compilation**: Combine four YouTube videos into a single meme video. 🎬
- **Web Interface**: Simple Flask web interface for user interaction. 🌐

## 🛠️ Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/MemeBot.git
    ```
2. Navigate to the project directory:
    ```bash
    cd MemeBot
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Usage

1. Run the Flask app:
    ```bash
    python main.py
    ```
2. Your flask app will be up and running at `http://0.0.0.0:8000`. 🌍

3. Enter four YouTube video URLs and generate your meme. 🎉

Alternatively, you can interact with the application via Postman or by sending a POST request using `curl`.

#### Sample `curl` request for `/generate-meme` endpoint:

```sh
curl -X POST "http://0.0.0.0:8000/generate-meme" -H "Content-Type: application/json" -d '{"urls": ["<URL1>", "<URL2>", "<URL3>", "<URL4>"]}'
```


## 🤝 Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Let's make MemeBot even better together! 💪

## 📜 License

This project is licensed under the MIT License.

## 📬 Contact

For any questions or suggestions, please open an issue. We love hearing from you! 💌